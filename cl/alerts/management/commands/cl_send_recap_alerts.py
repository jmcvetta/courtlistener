import copy
import datetime
import time
import traceback
from typing import Any, Type

import pytz
from asgiref.sync import async_to_sync
from django.contrib.auth.models import User
from django.http import QueryDict
from django.utils import timezone
from elasticsearch import Elasticsearch
from elasticsearch.exceptions import RequestError, TransportError
from elasticsearch_dsl import connections
from elasticsearch_dsl.response import Hit
from redis import Redis

from cl.alerts.models import Alert, ScheduledAlertHit
from cl.alerts.tasks import send_search_alert_emails
from cl.alerts.utils import (
    add_document_hit_to_alert_set,
    alert_hits_limit_reached,
    has_document_alert_hit_been_triggered,
    query_includes_rd_field,
    recap_document_hl_matched,
)
from cl.api.models import WebhookEventType
from cl.api.tasks import send_es_search_alert_webhook
from cl.lib.command_utils import VerboseCommand, logger
from cl.lib.date_time import dt_as_local_date
from cl.lib.elasticsearch_utils import do_es_sweep_alert_query
from cl.lib.redis_utils import get_redis_interface
from cl.search.documents import DocketDocument, RECAPSweepDocument
from cl.search.exception import (
    BadProximityQuery,
    UnbalancedParenthesesQuery,
    UnbalancedQuotesQuery,
)
from cl.search.models import SEARCH_TYPES, Docket
from cl.stats.utils import tally_stat
from cl.users.models import UserProfile


def get_task_status(task_id: str, es: Elasticsearch) -> dict[str, Any]:
    """Fetch the status of a task from Elasticsearch.

    :param task_id: The ID of the task to fetch the status for.
    :param es: The Elasticsearch client instance.
    :return: The status of the task if successful, or an empty dictionary if
    an error occurs.
    """
    try:
        return es.tasks.get(task_id=task_id)
    except (
        TransportError,
        ConnectionError,
        RequestError,
    ) as e:
        logger.error("Error getting sweep alert index task status: %s", e)
        return {}


def compute_estimated_remaining_time(
    initial_wait: float, start_time_millis: int, created: int, total: int
) -> float:
    """Compute the estimated remaining time for the re_index task to complete.

    :param initial_wait: The default wait time in seconds.
    :param start_time_millis: The start time in milliseconds epoch.
    :param created: The number of items created so far.
    :param total: The total number of items to be created.
    :return: The estimated remaining time in seconds. If the start time,
    created, or total are invalid, the initial default time is returned.
    """

    if start_time_millis is None or not created or not total:
        return initial_wait

    start_time = datetime.datetime.fromtimestamp(start_time_millis / 1000.0)
    time_now = datetime.datetime.now()
    estimated_time_remaining = max(
        datetime.timedelta(
            seconds=((time_now - start_time).total_seconds() / created)
            * (total - created)
        ).total_seconds(),
        initial_wait,
    )

    return estimated_time_remaining


def retrieve_task_info(task_info: dict[str, Any]) -> dict[str, Any]:
    """Retrieve task information from the given task dict.

    :param task_info: A dictionary containing the task status information.
    :return: A dictionary with the task completion status, created documents
    count, total documents count, and the task start time in milliseconds.
    Retrieve default values in case task_info is not valid.
    """

    if task_info:
        status = task_info["task"]["status"]
        return {
            "completed": task_info["completed"],
            "created": status["created"],
            "total": status["total"],
            "start_time_millis": task_info["task"]["start_time_in_millis"],
        }
    return {
        "completed": False,
        "created": 0,
        "total": 0,
        "start_time_millis": None,
    }


def index_daily_recap_documents(
    r: Redis,
    source_index_name: str,
    target_index: Type[RECAPSweepDocument],
    testing: bool = False,
) -> int:
    """Index Dockets added/modified during the day and all their RECAPDocuments
    and RECAPDocuments added/modified during the day and their parent Dockets.
    It uses the ES re_index API,

    :param r: Redis client instance.
    :param source_index_name: The source Elasticsearch index name from which
    documents will be queried.
    :param target_index: The target Elasticsearch index to which documents will
     be re-indexed.
    :param testing: Boolean flag for testing mode.
    :return: The total number of documents re-indexed.
    """

    if r.exists("alert_sweep:re_index_completed"):
        logger.info(
            "The re-index task has been completed and will be omitted."
        )
        # The re-indexing has been completed for the day. Abort it and proceed
        # with sending alerts.
        return 0

    if not r.exists("alert_sweep:query_date"):
        # In case of a failure, store the date when alerts should be queried in
        # Redis, so the command can be resumed.
        local_now = timezone.localtime().replace(tzinfo=None)
        local_midnight = local_now.replace(
            hour=0, minute=0, second=0, microsecond=0
        )
        r.set("alert_sweep:query_date", local_midnight.isoformat())

    else:
        # If "alert_sweep:query_date" already exists get it from Redis.
        local_midnight_str: str = str(r.get("alert_sweep:query_date"))
        local_midnight = datetime.datetime.fromisoformat(local_midnight_str)
        logger.info(f"Resuming re-indexing process for date: {local_midnight}")

    es = connections.get_connection()
    # Convert the local (PDT) midnight time to UTC
    local_timezone = pytz.timezone(timezone.get_current_timezone_name())
    local_midnight_localized = local_timezone.localize(local_midnight)
    local_midnight_utc = local_midnight_localized.astimezone(pytz.utc)
    next_day_utc = local_midnight_utc + datetime.timedelta(days=1)

    today_datetime_iso = local_midnight_utc.isoformat().replace("+00:00", "Z")
    next_day_utc_iso = next_day_utc.isoformat().replace("+00:00", "Z")
    # Re Index API query.
    query = {
        "bool": {
            "should": [
                # Dockets added/modified today
                {
                    "bool": {
                        "must": [
                            {
                                "range": {
                                    "timestamp": {
                                        "gte": today_datetime_iso,
                                        "lt": next_day_utc_iso,
                                    }
                                }
                            },
                            {"term": {"docket_child": "docket"}},
                        ]
                    }
                },
                # RECAPDocuments with parents added/modified today
                {
                    "has_parent": {
                        "parent_type": "docket",
                        "query": {
                            "range": {
                                "timestamp": {
                                    "gte": today_datetime_iso,
                                    "lt": next_day_utc_iso,
                                }
                            }
                        },
                    }
                },
                # RECAPDocuments added/modified today
                {
                    "bool": {
                        "must": [
                            {
                                "range": {
                                    "timestamp": {
                                        "gte": today_datetime_iso,
                                        "lt": next_day_utc_iso,
                                    }
                                }
                            },
                            {"term": {"docket_child": "recap_document"}},
                        ]
                    }
                },
                # Dockets that are parents of RECAPDocuments added/modified today
                {
                    "has_child": {
                        "type": "recap_document",
                        "query": {
                            "range": {
                                "timestamp": {
                                    "gte": today_datetime_iso,
                                    "lt": next_day_utc_iso,
                                }
                            }
                        },
                    }
                },
            ]
        }
    }

    if not r.exists("alert_sweep:task_id"):
        # Remove the index from the previous day and create a new one.
        target_index._index.delete(ignore=404)
        target_index.init()
        target_index_name = target_index._index._name

        # In case of a failure, store the task_id in Redis so the command
        # can be resumed.
        response = es.reindex(
            source={"index": source_index_name, "query": query},
            dest={"index": target_index_name},
            wait_for_completion=False,
            refresh=True,
        )
        # Store the task ID in Redis
        task_id = response["task"]
        r.set("alert_sweep:task_id", task_id)
        logger.info(f"Re-indexing task scheduled ID: {task_id}")
    else:
        task_id = r.get("alert_sweep:task_id")
        logger.info(f"Resuming re-index task ID: {task_id}")

    initial_wait = 0.01 if testing else 60.0
    time.sleep(initial_wait)
    get_task_info = retrieve_task_info(get_task_status(task_id, es))
    iterations_count = 0
    estimated_time_remaining = compute_estimated_remaining_time(
        initial_wait,
        get_task_info["start_time_millis"],
        get_task_info["created"],
        get_task_info["total"],
    )
    while not get_task_info["completed"]:
        logger.info(
            f"Task progress: {get_task_info['created']}/{get_task_info['total']} documents. "
            f"Estimated time to finish: {estimated_time_remaining} seconds."
        )
        task_info = get_task_status(task_id, es)
        get_task_info = retrieve_task_info(task_info)
        time.sleep(estimated_time_remaining)
        if task_info and not get_task_info["completed"]:
            estimated_time_remaining = compute_estimated_remaining_time(
                initial_wait,
                get_task_info["start_time_millis"],
                get_task_info["created"],
                get_task_info["total"],
            )
        if not task_info:
            iterations_count += 1
        if iterations_count > 10:
            logger.error(
                "Re_index alert sweep index task has failed: %s/%s",
                get_task_info["created"],
                get_task_info["total"],
            )
            break

    r.delete("alert_sweep:task_id")
    if not testing:
        r.set("alert_sweep:re_index_completed", 1, ex=3600 * 12)
    return get_task_info["total"]


def should_docket_hit_be_included(
    r: Redis, alert_id: int, docket_id: int
) -> bool:
    """Determine if a Docket alert should be triggered based on its
    date_modified and if the docket has triggered the alert previously.

    :param r: The Redis interface.
    :param alert_id: The ID of the alert.
    :param docket_id: The ID of the docket.
    :return: True if the Docket alert should be triggered, False otherwise.
    """
    docket = Docket.objects.filter(id=docket_id).only("date_modified").first()
    if not docket:
        return False
    if not has_document_alert_hit_been_triggered(r, alert_id, "d", docket_id):
        local_midnight_localized = timezone.localtime(
            timezone.make_aware(
                datetime.datetime.fromisoformat(
                    str(r.get("alert_sweep:query_date"))
                )
            )
        )
        date_modified_localized = dt_as_local_date(docket.date_modified)
        if date_modified_localized == local_midnight_localized.date():
            return True
    return False


def filter_rd_alert_hits(r: Redis, alert_id: int, rd_hits, check_rd_hl=False):
    """Filter RECAP document hits based on specified conditions.

    :param r: The Redis interface.
    :param alert_id: The ID of the alert.
    :param rd_hits: A list of RECAP document hits to be processed.
    :param check_rd_hl: A boolean indicating whether to check if the RECAP
    document hit matched RD HLs.
    :return: A list of RECAP document hits that meet all specified conditions.
    """

    rds_to_send = []
    for rd_hit in rd_hits:
        conditions = [
            not has_document_alert_hit_been_triggered(
                r, alert_id, "r", rd_hit["_source"]["id"]
            )
        ]
        if check_rd_hl:
            conditions.append(recap_document_hl_matched(rd_hit))
        if all(conditions):
            rds_to_send.append(rd_hit)
            add_document_hit_to_alert_set(
                r, alert_id, "r", rd_hit["_source"]["id"]
            )
    return rds_to_send


def query_alerts(
    search_params: QueryDict,
) -> tuple[list[Hit] | None, int | None]:
    try:
        search_query = RECAPSweepDocument.search()
        return do_es_sweep_alert_query(
            search_query,
            search_params,
        )
    except (
        UnbalancedParenthesesQuery,
        UnbalancedQuotesQuery,
        BadProximityQuery,
        TransportError,
        ConnectionError,
        RequestError,
    ):
        traceback.print_exc()
        logger.info(f"Search for this alert failed: {search_params}\n")
        return None, None


def process_alert_hits(
    r: Redis, results: list[Hit], search_params: QueryDict, alert_id: int
) -> list[Hit]:
    """Process alert hits by filtering and prepare the results to send based
    on alert conditions.

    :param r: The Redis instance.
    :param results: A list of Hit objects containing search results.
    :param search_params: Query parameters used for the search.
    :param alert_id: The ID of the alert being processed.
    :return: A list of Hit objects that are filtered and prepared to be sent.
    """

    includes_rd_fields = query_includes_rd_field(search_params)
    results_to_send = []
    if len(results) > 0:
        for hit in results:
            if not includes_rd_fields:
                # Possible Docket-only alert
                rds_to_send = filter_rd_alert_hits(
                    r, alert_id, hit["child_docs"], check_rd_hl=True
                )
                if rds_to_send:
                    # Cross-object query
                    hit["child_docs"] = rds_to_send
                    results_to_send.append(hit)
                elif should_docket_hit_be_included(r, alert_id, hit.docket_id):
                    # Docket-only alert
                    hit["child_docs"] = []
                    results_to_send.append(hit)
                    add_document_hit_to_alert_set(
                        r, alert_id, "d", hit.docket_id
                    )
            else:
                # RECAP-only alerts or cross-object alerts
                rds_to_send = filter_rd_alert_hits(
                    r, alert_id, hit["child_docs"]
                )
                if rds_to_send:
                    # Cross-object alert
                    hit["child_docs"] = rds_to_send
                    results_to_send.append(hit)
    return results_to_send


def send_search_alert_webhooks(
    user: UserProfile.user, results_to_send: list[Hit], alert_id: int
) -> None:
    """Send webhook events for search alerts if the user has SEARCH_ALERT
    endpoints enabled.

    :param user: The user object whose webhooks need to be checked.
    :param results_to_send: A list of Hit objects that contain the search
    results to be sent.
    :param alert_id: The Alert ID to be sent in the webhook.
    """
    user_webhooks = user.webhooks.filter(
        event_type=WebhookEventType.SEARCH_ALERT, enabled=True
    )
    for user_webhook in user_webhooks:
        send_es_search_alert_webhook.delay(
            results_to_send, user_webhook.pk, alert_id
        )


def query_and_send_alerts(r: Redis, rate: str) -> None:
    alert_users: UserProfile.user = User.objects.filter(
        alerts__rate=rate
    ).distinct()
    alerts_sent_count = 0
    now_time = datetime.datetime.now()
    for user in alert_users:
        if rate == Alert.REAL_TIME:
            if not user.profile.is_member:
                continue
        alerts = user.alerts.filter(rate=rate, alert_type=SEARCH_TYPES.RECAP)
        logger.info(f"Running alerts for user '{user}': {alerts}")

        hits = []
        alerts_to_update = []
        for alert in alerts:
            search_params = QueryDict(alert.query.encode(), mutable=True)
            results, _ = query_alerts(search_params)
            if not results:
                continue
            alerts_to_update.append(alert.pk)
            search_type = search_params.get("type", SEARCH_TYPES.RECAP)
            results_to_send = process_alert_hits(
                r, results, search_params, alert.pk
            )
            if results_to_send:
                hits.append(
                    [
                        alert,
                        search_type,
                        results_to_send,
                        len(results_to_send),
                    ]
                )
                alert.query_run = search_params.urlencode()  # type: ignore
                alert.date_last_hit = timezone.now()
                alert.save()

                # Send webhooks
                send_search_alert_webhooks(user, results_to_send, alert.pk)

        if hits:
            send_search_alert_emails.delay([(user.pk, hits)])
            alerts_sent_count += 1

        # Update Alert's date_last_hit in bulk.
        Alert.objects.filter(id__in=alerts_to_update).update(
            date_last_hit=now_time
        )
        async_to_sync(tally_stat)(f"alerts.sent.{rate}", inc=alerts_sent_count)
        logger.info(f"Sent {alerts_sent_count} {rate} email alerts.")


def query_and_schedule_alerts(r: Redis, rate: str):
    alert_users = User.objects.filter(alerts__rate=rate).distinct()
    for user in alert_users:
        alerts = user.alerts.filter(rate=rate, alert_type=SEARCH_TYPES.RECAP)
        logger.info(f"Running '{rate}' alerts for user '{user}': {alerts}")
        scheduled_hits_to_create = []
        for alert in alerts:
            search_params = QueryDict(alert.query.encode(), mutable=True)
            results, _ = query_alerts(search_params)
            if not results:
                continue
            results_to_send = process_alert_hits(
                r, results, search_params, alert.pk
            )
            if results_to_send:
                for hit in results_to_send:
                    # Schedule DAILY, WEEKLY and MONTHLY Alerts
                    if alert_hits_limit_reached(alert.pk, user.pk):
                        # Skip storing hits for this alert-user combination because
                        # the SCHEDULED_ALERT_HITS_LIMIT has been reached.
                        continue

                    child_result_objects = []
                    hit_copy = copy.deepcopy(hit)
                    if hasattr(hit_copy, "child_docs"):
                        for child_doc in hit_copy.child_docs:
                            child_result_objects.append(
                                child_doc["_source"].to_dict()
                            )
                    hit_copy["child_docs"] = child_result_objects
                    scheduled_hits_to_create.append(
                        ScheduledAlertHit(
                            user=user,
                            alert=alert,
                            document_content=hit_copy.to_dict(),
                        )
                    )
                    # Send webhooks
                    send_search_alert_webhooks(user, results_to_send, alert.pk)

        # Create scheduled WEEKLY and MONTHLY Alerts in bulk.
        if scheduled_hits_to_create:
            ScheduledAlertHit.objects.bulk_create(scheduled_hits_to_create)


class Command(VerboseCommand):
    """Query and re-index (into the RECAP sweep index) all the RECAP content
    that has changed during the current period, along with their related
    documents. Then use the RECAP sweep index to query and send real-time and
    daily RECAP alerts. Finally, schedule weekly and monthly RECAP alerts.
    """

    help = "Send RECAP Search Alerts."

    def add_arguments(self, parser):
        parser.add_argument(
            "--testing-mode",
            action="store_true",
            help="Use this flag for testing purposes.",
        )

    def handle(self, *args, **options):
        super().handle(*args, **options)
        testing_mode = options.get("testing_mode", False)
        r = get_redis_interface("CACHE")
        index_daily_recap_documents(
            r,
            DocketDocument._index._name,
            RECAPSweepDocument,
            testing=testing_mode,
        )
        query_and_send_alerts(r, Alert.REAL_TIME)
        query_and_send_alerts(r, Alert.DAILY)
        query_and_schedule_alerts(r, Alert.WEEKLY)
        query_and_schedule_alerts(r, Alert.MONTHLY)
        r.delete("alert_sweep:re_index_completed")
        r.delete("alert_sweep:query_date")
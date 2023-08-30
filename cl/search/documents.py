from datetime import datetime

from django.http import QueryDict
from django.template import loader
from django_elasticsearch_dsl import Document, fields
from elasticsearch_dsl import Join

from cl.alerts.models import Alert
from cl.audio.models import Audio
from cl.custom_filters.templatetags.text_filters import best_case_name
from cl.lib.command_utils import logger
from cl.lib.elasticsearch_utils import build_es_base_query
from cl.lib.fields import PercolatorField
from cl.lib.search_index_utils import null_map
from cl.lib.utils import deepgetattr
from cl.people_db.models import Education, Person, Position
from cl.search.es_indices import (
    oral_arguments_index,
    oral_arguments_percolator_index,
    parenthetical_group_index,
    people_db_index,
)
from cl.search.forms import SearchForm
from cl.search.models import Citation, ParentheticalGroup


@parenthetical_group_index.document
class ParentheticalGroupDocument(Document):
    author_id = fields.IntegerField(attr="opinion.author_id")
    caseName = fields.TextField(attr="opinion.cluster.case_name")
    citeCount = fields.IntegerField(attr="opinion.cluster.citation_count")
    citation = fields.ListField(
        fields.KeywordField(),
    )
    cites = fields.ListField(
        fields.IntegerField(),
    )
    cluster_id = fields.IntegerField(attr="opinion.cluster_id")
    court_id = fields.KeywordField(attr="opinion.cluster.docket.court.pk")
    dateFiled = fields.DateField(attr="opinion.cluster.date_filed")
    describing_opinion_cluster_id = fields.KeywordField(
        attr="representative.describing_opinion.cluster.id"
    )
    describing_opinion_cluster_slug = fields.KeywordField(
        attr="representative.describing_opinion.cluster.slug"
    )
    docket_id = fields.IntegerField(attr="opinion.cluster.docket_id")
    docketNumber = fields.KeywordField(
        attr="opinion.cluster.docket.docket_number"
    )
    judge = fields.TextField(
        attr="opinion.cluster.judges",
    )
    lexisCite = fields.ListField(
        fields.KeywordField(),
    )
    neutralCite = fields.ListField(
        fields.KeywordField(),
    )
    opinion_cluster_slug = fields.KeywordField(attr="opinion.cluster.slug")
    opinion_extracted_by_ocr = fields.BooleanField(
        attr="opinion.extracted_by_ocr"
    )
    panel_ids = fields.ListField(
        fields.IntegerField(),
    )
    representative_score = fields.KeywordField(attr="representative.score")
    representative_text = fields.TextField(
        attr="representative.text",
    )
    status = fields.KeywordField()
    suitNature = fields.TextField(
        attr="opinion.cluster.nature_of_suit",
    )

    class Django:
        model = ParentheticalGroup
        fields = ["score"]
        ignore_signals = True

    def prepare_citation(self, instance):
        return [str(cite) for cite in instance.opinion.cluster.citations.all()]

    def prepare_cites(self, instance):
        return [o.pk for o in instance.opinion.opinions_cited.all()]

    def prepare_lexisCite(self, instance):
        try:
            return str(
                instance.opinion.cluster.citations.filter(type=Citation.LEXIS)[
                    0
                ]
            )
        except IndexError:
            pass

    def prepare_neutralCite(self, instance):
        try:
            return str(
                instance.opinion.cluster.citations.filter(
                    type=Citation.NEUTRAL
                )[0]
            )
        except IndexError:
            pass

    def prepare_panel_ids(self, instance):
        return [judge.pk for judge in instance.opinion.cluster.panel.all()]

    def prepare_status(self, instance):
        return instance.opinion.cluster.get_precedential_status_display()


class AudioDocumentBase(Document):
    absolute_url = fields.KeywordField(attr="get_absolute_url", index=False)
    caseName = fields.TextField(
        analyzer="text_en_splitting_cl",
        fields={
            "exact": fields.TextField(analyzer="english_exact"),
        },
        search_analyzer="search_analyzer",
    )
    case_name_full = fields.TextField(
        attr="case_name_full",
        analyzer="text_en_splitting_cl",
        fields={
            "exact": fields.TextField(
                attr="case_name_full", analyzer="english_exact"
            ),
        },
        search_analyzer="search_analyzer",
    )
    court = fields.TextField(
        attr="docket.court.full_name",
        analyzer="text_en_splitting_cl",
        fields={
            "exact": fields.TextField(
                attr="docket.court.full_name", analyzer="english_exact"
            ),
        },
        search_analyzer="search_analyzer",
    )
    court_exact = fields.KeywordField(attr="docket.court.pk", index=False)
    court_id = fields.KeywordField(attr="docket.court.pk")
    court_id_text = fields.TextField(
        attr="docket.court.pk",
        analyzer="text_en_splitting_cl",
        search_analyzer="search_analyzer",
    )
    court_citation_string = fields.TextField(
        attr="docket.court.citation_string",
        analyzer="text_en_splitting_cl",
        search_analyzer="search_analyzer",
    )
    docket_id = fields.IntegerField(attr="docket.pk")
    dateArgued = fields.DateField(attr="docket.date_argued")
    dateReargued = fields.DateField(attr="docket.date_reargued")
    dateReargumentDenied = fields.DateField(
        attr="docket.date_reargument_denied"
    )
    dateArgued_text = fields.TextField(
        analyzer="text_en_splitting_cl",
        fields={
            "exact": fields.TextField(analyzer="english_exact"),
        },
        search_analyzer="search_analyzer",
    )
    dateReargued_text = fields.TextField(
        analyzer="text_en_splitting_cl",
        fields={
            "exact": fields.TextField(analyzer="english_exact"),
        },
        search_analyzer="search_analyzer",
    )
    dateReargumentDenied_text = fields.TextField(
        analyzer="text_en_splitting_cl",
        fields={
            "exact": fields.TextField(analyzer="english_exact"),
        },
        search_analyzer="search_analyzer",
    )
    docketNumber = fields.TextField(
        attr="docket.docket_number",
        analyzer="text_en_splitting_cl",
        fields={
            "exact": fields.TextField(
                attr="docket.docket_number", analyzer="english_exact"
            ),
        },
        search_analyzer="search_analyzer",
    )
    docket_slug = fields.KeywordField(attr="docket.slug", index=False)
    duration = fields.IntegerField(attr="duration", index=False)
    download_url = fields.KeywordField(attr="download_url", index=False)
    file_size_mp3 = fields.IntegerField(index=False)
    id = fields.IntegerField(attr="pk")
    judge = fields.TextField(
        attr="judges",
        analyzer="text_en_splitting_cl",
        fields={
            "exact": fields.TextField(attr="judges", analyzer="english_exact"),
        },
        search_analyzer="search_analyzer",
    )
    local_path = fields.KeywordField(index=False)
    pacer_case_id = fields.KeywordField(attr="docket.pacer_case_id")
    panel_ids = fields.ListField(
        fields.IntegerField(),
    )
    sha1 = fields.TextField(attr="sha1")
    source = fields.KeywordField(attr="source", index=False)
    text = fields.TextField(
        analyzer="text_en_splitting_cl",
        fields={
            "exact": fields.TextField(analyzer="english_exact"),
        },
        search_analyzer="search_analyzer",
    )
    timestamp = fields.DateField()


@oral_arguments_index.document
class AudioDocument(AudioDocumentBase):
    class Django:
        model = Audio
        ignore_signals = True

    def prepare_caseName(self, instance):
        return best_case_name(instance)

    def prepare_panel_ids(self, instance):
        return [judge.pk for judge in instance.panel.all()]

    def prepare_file_size_mp3(self, instance):
        if instance.local_path_mp3:
            return deepgetattr(instance, "local_path_mp3.size", None)

    def prepare_local_path(self, instance):
        if instance.local_path_mp3:
            return deepgetattr(instance, "local_path_mp3.name", None)

    def prepare_text(self, instance):
        if instance.stt_status == Audio.STT_COMPLETE:
            return instance.transcript

    def prepare_dateArgued_text(self, instance):
        if instance.docket.date_argued:
            return instance.docket.date_argued.strftime("%-d %B %Y")

    def prepare_dateReargued_text(self, instance):
        if instance.docket.date_reargued:
            return instance.docket.date_reargued.strftime("%-d %B %Y")

    def prepare_dateReargumentDenied_text(self, instance):
        if instance.docket.date_reargument_denied:
            return instance.docket.date_reargument_denied.strftime("%-d %B %Y")

    def prepare_timestamp(self, instance):
        return datetime.utcnow()


@oral_arguments_percolator_index.document
class AudioPercolator(AudioDocumentBase):
    rate = fields.KeywordField(attr="rate")
    date_created = fields.DateField(attr="date_created")
    percolator_query = PercolatorField()

    class Django:
        model = Alert
        ignore_signals = True

    def prepare_timestamp(self, instance):
        return datetime.utcnow()

    def prepare_percolator_query(self, instance):
        qd = QueryDict(instance.query.encode(), mutable=True)
        search_form = SearchForm(qd)
        if not search_form.is_valid():
            logger.warning(
                f"The query {qd} associated with Alert ID {instance.pk} is "
                f"invalid and was not indexed."
            )
            return None

        cd = search_form.cleaned_data
        search_query = AudioDocument.search()
        query = build_es_base_query(search_query, cd)
        return query.to_dict()["query"]


class PEOPLE_DOCS_TYPE_ID:
    """Returns an ID for its use in people_db_index child documents"""

    def __init__(self, instance_id: int):
        self.instance_id = instance_id

    @property
    def POSITION(self) -> str:
        return f"po_{self.instance_id}"

    @property
    def EDUCATION(self) -> str:
        return f"ed_{self.instance_id}"


@people_db_index.document
class PersonBaseDocument(Document):
    person_child = Join(relations={"person": ["position", "education"]})
    timestamp = fields.DateField()

    class Django:
        model = Person
        ignore_signals = True

    def prepare_timestamp(self, instance):
        return datetime.utcnow()


class EducationDocument(PersonBaseDocument):
    school = fields.TextField(
        attr="school.name",
        analyzer="text_en_splitting_cl",
        fields={
            "exact": fields.TextField(
                attr="school.name", analyzer="english_exact"
            ),
        },
        search_analyzer="search_analyzer",
    )
    degree_level = fields.KeywordField(attr="degree_level")
    degree_detail = fields.TextField(
        attr="degree_detail",
        analyzer="text_en_splitting_cl",
        fields={
            "exact": fields.TextField(
                attr="degree_detail", analyzer="english_exact"
            ),
        },
        search_analyzer="search_analyzer",
    )
    degree_year = fields.IntegerField(attr="degree_year")

    class Django:
        model = Education
        ignore_signals = True


class PositionDocument(PersonBaseDocument):
    court = fields.TextField(
        attr="court.short_name",
        analyzer="text_en_splitting_cl",
        fields={
            "exact": fields.TextField(
                attr="court.short_name", analyzer="english_exact"
            ),
        },
        search_analyzer="search_analyzer",
    )
    court_exact = fields.KeywordField(attr="court.pk")
    position_type = fields.KeywordField()
    appointer = fields.TextField(
        attr="appointer.person.name_full_reverse",
        analyzer="text_en_splitting_cl",
        fields={
            "exact": fields.TextField(
                attr="appointer.person.name_full_reverse",
                analyzer="english_exact",
            ),
        },
        search_analyzer="search_analyzer",
    )
    supervisor = fields.TextField(
        attr="supervisor.name_full_reverse",
        analyzer="text_en_splitting_cl",
        fields={
            "exact": fields.TextField(
                attr="supervisor.name_full_reverse", analyzer="english_exact"
            ),
        },
        search_analyzer="search_analyzer",
    )
    predecessor = fields.TextField(
        attr="predecessor.name_full_reverse",
        analyzer="text_en_splitting_cl",
        fields={
            "exact": fields.TextField(
                attr="predecessor.name_full_reverse", analyzer="english_exact"
            ),
        },
        search_analyzer="search_analyzer",
    )
    date_nominated = fields.DateField(attr="date_nominated")
    date_elected = fields.DateField(attr="date_elected")
    date_recess_appointment = fields.DateField(attr="date_recess_appointment")
    date_referred_to_judicial_committee = fields.DateField(
        attr="date_referred_to_judicial_committee"
    )
    date_judicial_committee_action = fields.DateField(
        attr="date_judicial_committee_action"
    )
    date_hearing = fields.DateField(attr="date_hearing")
    date_confirmation = fields.DateField(attr="date_confirmation")
    date_start = fields.DateField(attr="date_start")
    date_granularity_start = fields.KeywordField(attr="date_granularity_start")
    date_retirement = fields.DateField(attr="date_retirement")
    date_termination = fields.DateField(attr="date_termination")
    date_granularity_termination = fields.KeywordField(
        attr="date_granularity_termination"
    )
    judicial_committee_action = fields.KeywordField()
    nomination_process = fields.KeywordField()
    selection_method = fields.KeywordField()
    selection_method_id = fields.KeywordField(attr="how_selected")
    termination_reason = fields.KeywordField()
    text = fields.TextField(
        analyzer="text_en_splitting_cl",
        fields={
            "exact": fields.TextField(analyzer="english_exact"),
        },
        search_analyzer="search_analyzer",
    )

    class Django:
        model = Position
        ignore_signals = True

    def prepare_position_type(self, instance):
        return instance.get_position_type_display()

    def prepare_judicial_committee_action(self, instance):
        return instance.get_judicial_committee_action_display()

    def prepare_nomination_process(self, instance):
        return instance.get_nomination_process_display()

    def prepare_selection_method(self, instance):
        return instance.get_how_selected_display()

    def prepare_termination_reason(self, instance):
        return instance.get_termination_reason_display()

    def prepare_text(self, instance):
        text_template = loader.get_template("indexes/person_text.txt")
        return text_template.render({"item": instance}).translate(null_map)


class PersonDocument(PersonBaseDocument):
    id = fields.IntegerField(attr="pk")
    fjc_id = fields.IntegerField(attr="fjc_id")
    alias_ids = fields.ListField(
        fields.KeywordField(),
    )
    races = fields.ListField(
        fields.KeywordField(),
    )
    gender = fields.KeywordField()
    religion = fields.KeywordField(attr="religion")
    name = fields.TextField(
        attr="name_full",
        analyzer="text_en_splitting_cl",
        fields={
            "exact": fields.TextField(
                attr="name_full", analyzer="english_exact"
            ),
        },
        search_analyzer="search_analyzer",
    )
    name_reverse = fields.TextField(
        attr="name_reverse",
        analyzer="text_en_splitting_cl",
        fields={
            "exact": fields.TextField(
                attr="name_reverse", analyzer="english_exact"
            ),
        },
        search_analyzer="search_analyzer",
    )

    date_granularity_dob = fields.KeywordField(attr="date_granularity_dob")
    date_granularity_dod = fields.KeywordField(attr="date_granularity_dod")
    dob_city = fields.KeywordField(attr="dob_city")
    dob_state = fields.KeywordField()
    dob_state_id = fields.KeywordField(attr="dob_state")
    absolute_url = fields.KeywordField(attr="get_absolute_url")
    dob = fields.DateField(attr="date_dob")
    dod = fields.DateField(attr="date_dod")
    political_affiliation = fields.ListField(
        fields.KeywordField(),
    )
    political_affiliation_id = fields.ListField(
        fields.KeywordField(),
    )
    aba_rating = fields.ListField(
        fields.KeywordField(),
    )

    def save(self, **kwargs):
        self.person_child = "person"
        return super().save(**kwargs)

    def prepare_races(self, instance):
        return [r.get_race_display() for r in instance.race.all()]

    def prepare_alias_ids(self, instance):
        return [alias.pk for alias in instance.aliases.all()]

    def prepare_gender(self, instance):
        return instance.get_gender_display()

    def prepare_dob_state(self, instance):
        return instance.get_dob_state_display()

    def prepare_political_affiliation(self, instance):
        return [
            pa.get_political_party_display()
            for pa in instance.political_affiliations.all()
            if pa
        ]

    def prepare_political_affiliation_id(self, instance):
        return [
            pa.political_party
            for pa in instance.political_affiliations.all()
            if pa
        ]

    def prepare_aba_rating(self, instance):
        return [
            r.get_rating_display() for r in instance.aba_ratings.all() if r
        ]

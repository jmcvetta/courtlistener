# Generated by Django 4.2.1 on 2023-05-17 14:55

from django.db import migrations, models
import pgtrigger.compiler
import pgtrigger.migrations


class Migration(migrations.Migration):
    dependencies = [
        (
            "search",
            "0017_remove_bankruptcyinformation_update_or_delete_snapshot_update_and_more",
        ),
    ]

    operations = [
        pgtrigger.migrations.RemoveTrigger(
            model_name="opinioncluster",
            name="update_or_delete_snapshot_delete",
        ),
        pgtrigger.migrations.RemoveTrigger(
            model_name="opinioncluster",
            name="update_or_delete_snapshot_update",
        ),
        migrations.AddField(
            model_name="opinioncluster",
            name="arguments",
            field=models.TextField(
                blank=True,
                help_text="The attorney(s) and legal arguments presented as HTML text. This is primarily seen in older opinions and can contain case law cited and arguments presented to the judges.",
            ),
        ),
        migrations.AddField(
            model_name="opinioncluster",
            name="headmatter",
            field=models.TextField(
                blank=True,
                help_text="Headmatter is the content before an opinion in the Harvard CaseLaw import. This consists of summaries, headnotes, attorneys etc for the opinion.",
            ),
        ),
        migrations.AddField(
            model_name="opinionclusterevent",
            name="arguments",
            field=models.TextField(
                blank=True,
                help_text="The attorney(s) and legal arguments presented as HTML text. This is primarily seen in older opinions and can contain case law cited and arguments presented to the judges.",
            ),
        ),
        migrations.AddField(
            model_name="opinionclusterevent",
            name="headmatter",
            field=models.TextField(
                blank=True,
                help_text="Headmatter is the content before an opinion in the Harvard CaseLaw import. This consists of summaries, headnotes, attorneys etc for the opinion.",
            ),
        ),
        pgtrigger.migrations.AddTrigger(
            model_name="opinioncluster",
            trigger=pgtrigger.compiler.Trigger(
                name="update_or_delete_snapshot_update",
                sql=pgtrigger.compiler.UpsertTriggerSql(
                    condition='WHEN (OLD."id" IS DISTINCT FROM (NEW."id") OR OLD."date_created" IS DISTINCT FROM (NEW."date_created") OR OLD."docket_id" IS DISTINCT FROM (NEW."docket_id") OR OLD."judges" IS DISTINCT FROM (NEW."judges") OR OLD."date_filed" IS DISTINCT FROM (NEW."date_filed") OR OLD."date_filed_is_approximate" IS DISTINCT FROM (NEW."date_filed_is_approximate") OR OLD."slug" IS DISTINCT FROM (NEW."slug") OR OLD."case_name_short" IS DISTINCT FROM (NEW."case_name_short") OR OLD."case_name" IS DISTINCT FROM (NEW."case_name") OR OLD."case_name_full" IS DISTINCT FROM (NEW."case_name_full") OR OLD."scdb_id" IS DISTINCT FROM (NEW."scdb_id") OR OLD."scdb_decision_direction" IS DISTINCT FROM (NEW."scdb_decision_direction") OR OLD."scdb_votes_majority" IS DISTINCT FROM (NEW."scdb_votes_majority") OR OLD."scdb_votes_minority" IS DISTINCT FROM (NEW."scdb_votes_minority") OR OLD."source" IS DISTINCT FROM (NEW."source") OR OLD."procedural_history" IS DISTINCT FROM (NEW."procedural_history") OR OLD."attorneys" IS DISTINCT FROM (NEW."attorneys") OR OLD."nature_of_suit" IS DISTINCT FROM (NEW."nature_of_suit") OR OLD."posture" IS DISTINCT FROM (NEW."posture") OR OLD."syllabus" IS DISTINCT FROM (NEW."syllabus") OR OLD."headnotes" IS DISTINCT FROM (NEW."headnotes") OR OLD."summary" IS DISTINCT FROM (NEW."summary") OR OLD."disposition" IS DISTINCT FROM (NEW."disposition") OR OLD."history" IS DISTINCT FROM (NEW."history") OR OLD."other_dates" IS DISTINCT FROM (NEW."other_dates") OR OLD."cross_reference" IS DISTINCT FROM (NEW."cross_reference") OR OLD."correction" IS DISTINCT FROM (NEW."correction") OR OLD."citation_count" IS DISTINCT FROM (NEW."citation_count") OR OLD."precedential_status" IS DISTINCT FROM (NEW."precedential_status") OR OLD."date_blocked" IS DISTINCT FROM (NEW."date_blocked") OR OLD."blocked" IS DISTINCT FROM (NEW."blocked") OR OLD."filepath_json_harvard" IS DISTINCT FROM (NEW."filepath_json_harvard") OR OLD."arguments" IS DISTINCT FROM (NEW."arguments") OR OLD."headmatter" IS DISTINCT FROM (NEW."headmatter"))',
                    func='INSERT INTO "search_opinionclusterevent" ("arguments", "attorneys", "blocked", "case_name", "case_name_full", "case_name_short", "citation_count", "correction", "cross_reference", "date_blocked", "date_created", "date_filed", "date_filed_is_approximate", "date_modified", "disposition", "docket_id", "filepath_json_harvard", "headmatter", "headnotes", "history", "id", "judges", "nature_of_suit", "other_dates", "pgh_context_id", "pgh_created_at", "pgh_label", "pgh_obj_id", "posture", "precedential_status", "procedural_history", "scdb_decision_direction", "scdb_id", "scdb_votes_majority", "scdb_votes_minority", "slug", "source", "summary", "syllabus") VALUES (OLD."arguments", OLD."attorneys", OLD."blocked", OLD."case_name", OLD."case_name_full", OLD."case_name_short", OLD."citation_count", OLD."correction", OLD."cross_reference", OLD."date_blocked", OLD."date_created", OLD."date_filed", OLD."date_filed_is_approximate", OLD."date_modified", OLD."disposition", OLD."docket_id", OLD."filepath_json_harvard", OLD."headmatter", OLD."headnotes", OLD."history", OLD."id", OLD."judges", OLD."nature_of_suit", OLD."other_dates", _pgh_attach_context(), NOW(), \'update_or_delete_snapshot\', OLD."id", OLD."posture", OLD."precedential_status", OLD."procedural_history", OLD."scdb_decision_direction", OLD."scdb_id", OLD."scdb_votes_majority", OLD."scdb_votes_minority", OLD."slug", OLD."source", OLD."summary", OLD."syllabus"); RETURN NULL;',
                    hash="a186ab65e2b0b6da774524ca6948808bf68a4f93",
                    operation="UPDATE",
                    pgid="pgtrigger_update_or_delete_snapshot_update_6a181",
                    table="search_opinioncluster",
                    when="AFTER",
                ),
            ),
        ),
        pgtrigger.migrations.AddTrigger(
            model_name="opinioncluster",
            trigger=pgtrigger.compiler.Trigger(
                name="update_or_delete_snapshot_delete",
                sql=pgtrigger.compiler.UpsertTriggerSql(
                    func='INSERT INTO "search_opinionclusterevent" ("arguments", "attorneys", "blocked", "case_name", "case_name_full", "case_name_short", "citation_count", "correction", "cross_reference", "date_blocked", "date_created", "date_filed", "date_filed_is_approximate", "date_modified", "disposition", "docket_id", "filepath_json_harvard", "headmatter", "headnotes", "history", "id", "judges", "nature_of_suit", "other_dates", "pgh_context_id", "pgh_created_at", "pgh_label", "pgh_obj_id", "posture", "precedential_status", "procedural_history", "scdb_decision_direction", "scdb_id", "scdb_votes_majority", "scdb_votes_minority", "slug", "source", "summary", "syllabus") VALUES (OLD."arguments", OLD."attorneys", OLD."blocked", OLD."case_name", OLD."case_name_full", OLD."case_name_short", OLD."citation_count", OLD."correction", OLD."cross_reference", OLD."date_blocked", OLD."date_created", OLD."date_filed", OLD."date_filed_is_approximate", OLD."date_modified", OLD."disposition", OLD."docket_id", OLD."filepath_json_harvard", OLD."headmatter", OLD."headnotes", OLD."history", OLD."id", OLD."judges", OLD."nature_of_suit", OLD."other_dates", _pgh_attach_context(), NOW(), \'update_or_delete_snapshot\', OLD."id", OLD."posture", OLD."precedential_status", OLD."procedural_history", OLD."scdb_decision_direction", OLD."scdb_id", OLD."scdb_votes_majority", OLD."scdb_votes_minority", OLD."slug", OLD."source", OLD."summary", OLD."syllabus"); RETURN NULL;',
                    hash="efad05406fc64c608bbade46146fd2dbfd61692f",
                    operation="DELETE",
                    pgid="pgtrigger_update_or_delete_snapshot_delete_58fe8",
                    table="search_opinioncluster",
                    when="AFTER",
                ),
            ),
        ),
    ]

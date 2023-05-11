# Generated by Django 4.2.1 on 2023-05-11 17:58

from django.db import migrations, models
import django.db.models.deletion
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
        migrations.CreateModel(
            name="ClusterStub",
            fields=[
                (
                    "id",
                    models.AutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "date_created",
                    models.DateTimeField(
                        auto_now_add=True,
                        db_index=True,
                        help_text="The moment when the item was created.",
                    ),
                ),
                (
                    "date_modified",
                    models.DateTimeField(
                        auto_now=True,
                        db_index=True,
                        help_text="The last moment when the item was modified. A value in year 1750 indicates the value is unknown",
                    ),
                ),
                (
                    "case_name",
                    models.TextField(
                        blank=True, help_text="The standard name of the case"
                    ),
                ),
                (
                    "case_name_full",
                    models.TextField(
                        blank=True, help_text="The full unabridged case name"
                    ),
                ),
                (
                    "date_filed",
                    models.DateField(
                        blank=True,
                        help_text="The date the case was filed",
                        null=True,
                    ),
                ),
                (
                    "date_decided",
                    models.DateField(
                        blank=True,
                        help_text="The date the opinion was decided",
                        null=True,
                    ),
                ),
                (
                    "date_argued",
                    models.DateField(
                        blank=True,
                        help_text="The date the opinion was argued",
                        null=True,
                    ),
                ),
                (
                    "date_revised",
                    models.DateField(
                        blank=True,
                        help_text="The date the opinion was revised",
                        null=True,
                    ),
                ),
                (
                    "court_str",
                    models.TextField(
                        blank=True, help_text="Court name as a string"
                    ),
                ),
                (
                    "docket_number",
                    models.TextField(
                        blank=True,
                        help_text="The docket number(s) associated with the opinion or case",
                    ),
                ),
                (
                    "raw_citations",
                    models.TextField(
                        blank=True,
                        help_text="Text value of the citation or citations",
                    ),
                ),
                (
                    "citations",
                    models.JSONField(
                        blank=True,
                        help_text="Citations found by eyecite. Used when we have citation values that are not allowed in our citation table",
                        null=True,
                    ),
                ),
            ],
            options={
                "verbose_name_plural": "OpinionCluster stubs",
            },
        ),
        pgtrigger.migrations.RemoveTrigger(
            model_name="citation",
            name="update_or_delete_snapshot_update",
        ),
        pgtrigger.migrations.RemoveTrigger(
            model_name="citation",
            name="update_or_delete_snapshot_delete",
        ),
        migrations.AlterField(
            model_name="citation",
            name="cluster",
            field=models.ForeignKey(
                blank=True,
                help_text="The cluster that the citation applies to",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="citations",
                to="search.opinioncluster",
            ),
        ),
        migrations.AlterField(
            model_name="citationevent",
            name="cluster",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                help_text="The cluster that the citation applies to",
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                related_query_name="+",
                to="search.opinioncluster",
            ),
        ),
        pgtrigger.migrations.AddTrigger(
            model_name="citation",
            trigger=pgtrigger.compiler.Trigger(
                name="update_or_delete_snapshot_update",
                sql=pgtrigger.compiler.UpsertTriggerSql(
                    condition="WHEN (OLD.* IS DISTINCT FROM NEW.*)",
                    func='INSERT INTO "search_citationevent" ("cluster_id", "cluster_stub_id", "id", "page", "pgh_context_id", "pgh_created_at", "pgh_label", "pgh_obj_id", "reporter", "type", "volume") VALUES (OLD."cluster_id", OLD."cluster_stub_id", OLD."id", OLD."page", _pgh_attach_context(), NOW(), \'update_or_delete_snapshot\', OLD."id", OLD."reporter", OLD."type", OLD."volume"); RETURN NULL;',
                    hash="a81041881c0deae3a0212fad2676c613d2e164fc",
                    operation="UPDATE",
                    pgid="pgtrigger_update_or_delete_snapshot_update_8f120",
                    table="search_citation",
                    when="AFTER",
                ),
            ),
        ),
        pgtrigger.migrations.AddTrigger(
            model_name="citation",
            trigger=pgtrigger.compiler.Trigger(
                name="update_or_delete_snapshot_delete",
                sql=pgtrigger.compiler.UpsertTriggerSql(
                    func='INSERT INTO "search_citationevent" ("cluster_id", "cluster_stub_id", "id", "page", "pgh_context_id", "pgh_created_at", "pgh_label", "pgh_obj_id", "reporter", "type", "volume") VALUES (OLD."cluster_id", OLD."cluster_stub_id", OLD."id", OLD."page", _pgh_attach_context(), NOW(), \'update_or_delete_snapshot\', OLD."id", OLD."reporter", OLD."type", OLD."volume"); RETURN NULL;',
                    hash="2f3ba1f8757d6bdfca6d9f54cd5c630ebc7d085d",
                    operation="DELETE",
                    pgid="pgtrigger_update_or_delete_snapshot_delete_9631d",
                    table="search_citation",
                    when="AFTER",
                ),
            ),
        ),
        migrations.AddField(
            model_name="clusterstub",
            name="court",
            field=models.ForeignKey(
                blank=True,
                help_text="The court where the opinion cluster was filed",
                null=True,
                on_delete=django.db.models.deletion.RESTRICT,
                to="search.court",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="citation",
            unique_together={("cluster", "volume", "reporter", "page")},
        ),
        migrations.AddField(
            model_name="citation",
            name="cluster_stub",
            field=models.ForeignKey(
                blank=True,
                help_text="The stub that the citation applies to",
                null=True,
                on_delete=django.db.models.deletion.CASCADE,
                related_name="stub_citations",
                to="search.clusterstub",
            ),
        ),
        migrations.AddField(
            model_name="citationevent",
            name="cluster_stub",
            field=models.ForeignKey(
                blank=True,
                db_constraint=False,
                help_text="The stub that the citation applies to",
                null=True,
                on_delete=django.db.models.deletion.DO_NOTHING,
                related_name="+",
                related_query_name="+",
                to="search.clusterstub",
            ),
        ),
        migrations.AlterUniqueTogether(
            name="citation",
            unique_together={
                ("cluster", "volume", "reporter", "page"),
                ("cluster_stub", "volume", "reporter", "page"),
            },
        ),
        migrations.AddConstraint(
            model_name="citation",
            constraint=models.CheckConstraint(
                check=models.Q(
                    ("cluster__isnull", False),
                    ("cluster_stub__isnull", False),
                    _connector="OR",
                ),
                name="not_both_null",
            ),
        ),
    ]

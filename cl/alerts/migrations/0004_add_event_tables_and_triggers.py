# Generated by Django 3.2.16 on 2023-01-25 23:56

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion
import pgtrigger.compiler
import pgtrigger.migrations


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('search', '0011_add_event_tables_and_triggers'),
        ('pghistory', '0005_events_middlewareevents'),
        ('alerts', '0003_add_docket_alert_date_modified'),
    ]

    operations = [
        migrations.CreateModel(
            name='AlertEvent',
            fields=[
                ('pgh_id', models.AutoField(primary_key=True, serialize=False)),
                ('pgh_created_at', models.DateTimeField(auto_now_add=True)),
                ('pgh_label', models.TextField(help_text='The event label.')),
                ('id', models.IntegerField()),
                ('date_created', models.DateTimeField(auto_now_add=True, help_text='The moment when the item was created.')),
                ('date_modified', models.DateTimeField(auto_now=True, help_text='The last moment when the item was modified. A value in year 1750 indicates the value is unknown')),
                ('date_last_hit', models.DateTimeField(blank=True, null=True, verbose_name='time of last trigger')),
                ('name', models.CharField(max_length=75, verbose_name='a name for the alert')),
                ('query', models.CharField(max_length=2500, verbose_name='the text of an alert created by a user')),
                ('rate', models.CharField(choices=[('rt', 'Real Time'), ('dly', 'Daily'), ('wly', 'Weekly'), ('mly', 'Monthly'), ('off', 'Off')], max_length=10, verbose_name='the rate chosen by the user for the alert')),
                ('secret_key', models.CharField(max_length=40, verbose_name='A key to be used in links to access the alert without having to log in. Can be used for a variety of purposes.')),
            ],
            options={
                'abstract': False,
            },
        ),
        migrations.CreateModel(
            name='DocketAlertEvent',
            fields=[
                ('pgh_id', models.AutoField(primary_key=True, serialize=False)),
                ('pgh_created_at', models.DateTimeField(auto_now_add=True)),
                ('pgh_label', models.TextField(help_text='The event label.')),
                ('id', models.IntegerField()),
                ('date_created', models.DateTimeField(auto_now_add=True, help_text='The moment when the item was created.')),
                ('date_modified', models.DateTimeField(auto_now=True, help_text='The last moment when the item was modified. A value in year 1750 indicates the value is unknown')),
                ('date_last_hit', models.DateTimeField(blank=True, null=True, verbose_name='time of last trigger')),
                ('secret_key', models.CharField(max_length=40, verbose_name='A key to be used in links to access the alert without having to log in. Can be used for a variety of purposes.')),
                ('alert_type', models.SmallIntegerField(choices=[(0, 'Unsubscription'), (1, 'Subscription')], default=1, help_text='The subscription type assigned, Unsubscription or Subscription.')),
            ],
            options={
                'abstract': False,
            },
        ),
        pgtrigger.migrations.AddTrigger(
            model_name='alert',
            trigger=pgtrigger.compiler.Trigger(name='snapshot_insert', sql=pgtrigger.compiler.UpsertTriggerSql(func='INSERT INTO "alerts_alertevent" ("date_created", "date_last_hit", "date_modified", "id", "name", "pgh_context_id", "pgh_created_at", "pgh_label", "pgh_obj_id", "query", "rate", "secret_key", "user_id") VALUES (NEW."date_created", NEW."date_last_hit", NEW."date_modified", NEW."id", NEW."name", _pgh_attach_context(), NOW(), \'snapshot\', NEW."id", NEW."query", NEW."rate", NEW."secret_key", NEW."user_id"); RETURN NULL;', hash='907312d0810a79ed5bd1affecfd8bbbab449a03a', operation='INSERT', pgid='pgtrigger_snapshot_insert_cff3d', table='alerts_alert', when='AFTER')),
        ),
        pgtrigger.migrations.AddTrigger(
            model_name='alert',
            trigger=pgtrigger.compiler.Trigger(name='snapshot_update', sql=pgtrigger.compiler.UpsertTriggerSql(condition='WHEN (OLD.* IS DISTINCT FROM NEW.*)', func='INSERT INTO "alerts_alertevent" ("date_created", "date_last_hit", "date_modified", "id", "name", "pgh_context_id", "pgh_created_at", "pgh_label", "pgh_obj_id", "query", "rate", "secret_key", "user_id") VALUES (NEW."date_created", NEW."date_last_hit", NEW."date_modified", NEW."id", NEW."name", _pgh_attach_context(), NOW(), \'snapshot\', NEW."id", NEW."query", NEW."rate", NEW."secret_key", NEW."user_id"); RETURN NULL;', hash='f7e2b2f927a09fa01ed53ade96cab4e71a821734', operation='UPDATE', pgid='pgtrigger_snapshot_update_691d5', table='alerts_alert', when='AFTER')),
        ),
        pgtrigger.migrations.AddTrigger(
            model_name='docketalert',
            trigger=pgtrigger.compiler.Trigger(name='snapshot_insert', sql=pgtrigger.compiler.UpsertTriggerSql(func='INSERT INTO "alerts_docketalertevent" ("alert_type", "date_created", "date_last_hit", "date_modified", "docket_id", "id", "pgh_context_id", "pgh_created_at", "pgh_label", "pgh_obj_id", "secret_key", "user_id") VALUES (NEW."alert_type", NEW."date_created", NEW."date_last_hit", NEW."date_modified", NEW."docket_id", NEW."id", _pgh_attach_context(), NOW(), \'snapshot\', NEW."id", NEW."secret_key", NEW."user_id"); RETURN NULL;', hash='eede0c0fc7c8775ba94bb0a6d9920b9e2b540103', operation='INSERT', pgid='pgtrigger_snapshot_insert_f3fdd', table='alerts_docketalert', when='AFTER')),
        ),
        pgtrigger.migrations.AddTrigger(
            model_name='docketalert',
            trigger=pgtrigger.compiler.Trigger(name='snapshot_update', sql=pgtrigger.compiler.UpsertTriggerSql(condition='WHEN (OLD.* IS DISTINCT FROM NEW.*)', func='INSERT INTO "alerts_docketalertevent" ("alert_type", "date_created", "date_last_hit", "date_modified", "docket_id", "id", "pgh_context_id", "pgh_created_at", "pgh_label", "pgh_obj_id", "secret_key", "user_id") VALUES (NEW."alert_type", NEW."date_created", NEW."date_last_hit", NEW."date_modified", NEW."docket_id", NEW."id", _pgh_attach_context(), NOW(), \'snapshot\', NEW."id", NEW."secret_key", NEW."user_id"); RETURN NULL;', hash='03cc481405ab3524896a2816845b09ccfb0ba95f', operation='UPDATE', pgid='pgtrigger_snapshot_update_2c804', table='alerts_docketalert', when='AFTER')),
        ),
        migrations.AddField(
            model_name='docketalertevent',
            name='docket',
            field=models.ForeignKey(db_constraint=False, help_text='The docket that we are subscribed to.', on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', related_query_name='+', to='search.docket'),
        ),
        migrations.AddField(
            model_name='docketalertevent',
            name='pgh_context',
            field=models.ForeignKey(db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='pghistory.context'),
        ),
        migrations.AddField(
            model_name='docketalertevent',
            name='pgh_obj',
            field=models.ForeignKey(db_constraint=False, on_delete=django.db.models.deletion.DO_NOTHING, related_name='event', to='alerts.docketalert'),
        ),
        migrations.AddField(
            model_name='docketalertevent',
            name='user',
            field=models.ForeignKey(db_constraint=False, help_text='The user that is subscribed to the docket.', on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', related_query_name='+', to=settings.AUTH_USER_MODEL),
        ),
        migrations.AddField(
            model_name='alertevent',
            name='pgh_context',
            field=models.ForeignKey(db_constraint=False, null=True, on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', to='pghistory.context'),
        ),
        migrations.AddField(
            model_name='alertevent',
            name='pgh_obj',
            field=models.ForeignKey(db_constraint=False, on_delete=django.db.models.deletion.DO_NOTHING, related_name='event', to='alerts.alert'),
        ),
        migrations.AddField(
            model_name='alertevent',
            name='user',
            field=models.ForeignKey(db_constraint=False, help_text='The user that created the item', on_delete=django.db.models.deletion.DO_NOTHING, related_name='+', related_query_name='+', to=settings.AUTH_USER_MODEL),
        ),
    ]
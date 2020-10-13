# -*- coding: utf-8 -*-
# Generated by Django 1.11.29 on 2020-07-23 05:10
"""
- Add field date_completed to person
- Add field dob_country to person
- Add field dod_country to person
- Add field sector to position
- Alter field extra_info on party (update help_text, noop)
- Alter field date_start on position (make it nullable)
- Alter field position_type on position (add a few more choices, noop)
"""




from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people_db', '0042_noop_update_help_text'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='date_completed',
            field=models.DateTimeField(blank=True, help_text='Whenever an editor last decided that a profile was complete in some sense.', null=True),
        ),
        migrations.AddField(
            model_name='person',
            name='dob_country',
            field=models.CharField(blank=True, default='United States', help_text='The country where the person was born.', max_length=50),
        ),
        migrations.AddField(
            model_name='person',
            name='dod_country',
            field=models.CharField(blank=True, default='United States', help_text='The country where the person died.', max_length=50),
        ),
        migrations.AddField(
            model_name='position',
            name='sector',
            field=models.SmallIntegerField(blank=True, choices=[(1, 'Private sector'), (2, 'Public sector')], default=None, help_text='Whether the job was private or public sector.', null=True),
        ),
        # Noop
        migrations.AlterField(
            model_name='party',
            name='extra_info',
            field=models.TextField(db_index=True, help_text='Prior to March, 2018, this field briefly held additional info from PACER about particular parties. That was a modelling mistake and the information has been moved to the PartyType.extra_info field instead. This field will be removed in October, 2020.'),
        ),
        migrations.AlterField(
            model_name='position',
            name='date_start',
            field=models.DateField(blank=True, db_index=True, help_text='The date the position starts active duty.', null=True),
        ),
        migrations.AlterField(
            model_name='position',
            name='position_type',
            field=models.CharField(blank=True, choices=[('Judge', (('act-jud', 'Acting Judge'), ('act-pres-jud', 'Acting Presiding Judge'), ('ass-jud', 'Associate Judge'), ('ass-c-jud', 'Associate Chief Judge'), ('ass-pres-jud', 'Associate Presiding Judge'), ('jud', 'Judge'), ('jus', 'Justice'), ('c-jud', 'Chief Judge'), ('c-jus', 'Chief Justice'), ('c-spec-m', 'Chief Special Master'), ('pres-jud', 'Presiding Judge'), ('pres-jus', 'Presiding Justice'), ('com', 'Commissioner'), ('com-dep', 'Deputy Commissioner'), ('jud-pt', 'Judge Pro Tem'), ('jus-pt', 'Justice Pro Tem'), ('ref-jud-tr', 'Judge Trial Referee'), ('ref-off', 'Official Referee'), ('ref-state-trial', 'State Trial Referee'), ('ret-act-jus', 'Active Retired Justice'), ('ret-ass-jud', 'Retired Associate Judge'), ('ret-c-jud', 'Retired Chief Judge'), ('ret-jus', 'Retired Justice'), ('ret-senior-jud', 'Senior Judge'), ('mag', 'Magistrate'), ('c-mag', 'Chief Magistrate'), ('pres-mag', 'Presiding Magistrate'), ('mag-pt', 'Magistrate Pro Tem'), ('mag-rc', 'Magistrate (Recalled)'), ('mag-part-time', 'Magistrate (Part-Time)'), ('spec-chair', 'Special Chairman'), ('spec-jud', 'Special Judge'), ('spec-m', 'Special Master'), ('spec-scjcbc', 'Special Superior Court Judge for Complex Business Cases'), ('chair', 'Chairman'), ('chan', 'Chancellor'), ('presi-jud', 'President'), ('res-jud', 'Reserve Judge'), ('trial-jud', 'Trial Judge'), ('vice-chan', 'Vice Chancellor'), ('vice-cj', 'Vice Chief Judge'))), ('Attorney General', (('att-gen', 'Attorney General'), ('att-gen-ass', 'Assistant Attorney General'), ('att-gen-ass-spec', 'Special Assistant Attorney General'), ('sen-counsel', 'Senior Counsel'), ('dep-sol-gen', 'Deputy Solicitor General'))), ('Appointing Authority', (('pres', 'President of the United States'), ('gov', 'Governor'))), ('Clerkships', (('clerk', 'Clerk'), ('clerk-chief-dep', 'Chief Deputy Clerk'), ('staff-atty', 'Staff Attorney'))), ('prof', 'Professor'), ('Practitioner', 'Practitioner'), ('Prosecutor', 'Prosecutor'), ('Public Defender', 'Public Defender'), ('legis', 'Legislator')], help_text='If this is a judicial position, this indicates the role the person had. This field may be blank if job_title is complete instead.', max_length=20, null=True),
        ),
    ]

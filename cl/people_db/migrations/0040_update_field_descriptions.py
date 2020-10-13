# -*- coding: utf-8 -*-
# Generated by Django 1.11.22 on 2019-07-31 02:41


from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('people_db', '0039_add_role_raw'),
    ]

    operations = [
        migrations.AlterField(
            model_name='partytype',
            name='name',
            field=models.CharField(db_index=True, help_text='The name of the type (Defendant, Plaintiff, etc.)', max_length=100),
        ),
        migrations.AlterField(
            model_name='politicalaffiliation',
            name='political_party',
            field=models.CharField(choices=[('d', 'Democratic'), ('r', 'Republican'), ('i', 'Independent'), ('g', 'Green'), ('l', 'Libertarian'), ('f', 'Federalist'), ('w', 'Whig'), ('j', 'Jeffersonian Republican'), ('u', 'National Union')], help_text='The political party the person is affiliated with.', max_length=5),
        ),
    ]

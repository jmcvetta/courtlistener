# Generated by Django 4.2 on 2023-05-02 00:29

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ("recap", "0011_alter_processingqueue_upload_type_noop"),
    ]

    operations = [
        migrations.RenameIndex(
            model_name="fjcintegrateddatabase",
            new_name="recap_fjcin_distric_731c7b_idx",
            old_fields=("district", "docket_number"),
        ),
    ]

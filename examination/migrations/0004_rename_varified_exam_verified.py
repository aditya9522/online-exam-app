# Generated by Django 5.0.7 on 2025-02-05 07:03

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('examination', '0003_exam_varified'),
    ]

    operations = [
        migrations.RenameField(
            model_name='exam',
            old_name='varified',
            new_name='verified',
        ),
    ]

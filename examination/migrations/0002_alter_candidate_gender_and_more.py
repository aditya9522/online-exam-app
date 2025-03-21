# Generated by Django 5.0.7 on 2025-01-31 19:39

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('examination', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='candidate',
            name='gender',
            field=models.CharField(choices=[('Male', 'Male'), ('Female', 'Female'), ('Others', 'Others')], max_length=10),
        ),
        migrations.AlterField(
            model_name='candidate',
            name='profession_type',
            field=models.CharField(choices=[('Student', 'Student'), ('Fresher', 'Fresher'), ('Experienced', 'Experienced')], max_length=15),
        ),
        migrations.AlterField(
            model_name='questionset',
            name='level',
            field=models.CharField(choices=[('Easy', 'Easy'), ('Medium', 'Medium'), ('Hard', 'Hard'), ('Hybrid', 'Hybrid')], max_length=10),
        ),
    ]

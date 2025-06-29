# Generated by Django 5.2.1 on 2025-06-26 12:16

import datetime
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0034_university_alter_job_deadline_prospectus'),
    ]

    operations = [
        migrations.AddField(
            model_name='university',
            name='acronym',
            field=models.CharField(blank=True, help_text='e.g., TUT, UJ, UCT', max_length=20),
        ),
        migrations.AlterField(
            model_name='job',
            name='deadline',
            field=models.DateField(default=datetime.datetime(2025, 12, 23, 12, 16, 27, 266030, tzinfo=datetime.timezone.utc)),
        ),
    ]

# Generated by Django 5.2.1 on 2025-06-12 13:42

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0016_salaryrequest_requests_count_and_more'),
    ]

    operations = [
        migrations.AlterField(
            model_name='salaryrequest',
            name='job_title',
            field=models.CharField(max_length=255, null=True, unique=True),
        ),
    ]

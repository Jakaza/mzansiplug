# Generated by Django 5.2.1 on 2025-06-12 08:28

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0006_job_experience_level_job_job_type_job_salary_and_more'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='job',
            name='category',
        ),
        migrations.AddField(
            model_name='job',
            name='categories',
            field=models.ManyToManyField(related_name='jobs', to='base.category'),
        ),
    ]

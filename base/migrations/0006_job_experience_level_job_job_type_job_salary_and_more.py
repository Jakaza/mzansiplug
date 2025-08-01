# Generated by Django 5.2.1 on 2025-06-10 09:53

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('base', '0005_job_external_company_name'),
    ]

    operations = [
        migrations.AddField(
            model_name='job',
            name='experience_level',
            field=models.CharField(blank=True, choices=[('entry', 'Entry'), ('mid', 'Mid'), ('senior', 'Senior'), ('executive', 'Executive'), ('manager', 'Manager')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='job_type',
            field=models.CharField(blank=True, choices=[('full_time', 'Full Time'), ('part_time', 'Part Time'), ('contract', 'Contract'), ('internship', 'Internship'), ('remote', 'Remote'), ('hybrid', 'Hybrid')], max_length=20, null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='salary',
            field=models.DecimalField(blank=True, decimal_places=2, max_digits=10, null=True),
        ),
        migrations.AddField(
            model_name='job',
            name='views',
            field=models.PositiveIntegerField(default=0),
        ),
    ]

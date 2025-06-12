from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.conf import settings
from ckeditor.fields import RichTextField


class User(AbstractUser):
    is_company = models.BooleanField(default=False)

    def __str__(self):
        return self.username


class CompanyProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    company_name = models.CharField(max_length=255)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.company_name


class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Job(models.Model):
    JOB_TYPE = (
        ('internal', 'Internal'),
        ('external', 'External'),
    )

    JOB_TYPE_CHOICES = [
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('remote', 'Remote'),
        ('hybrid', 'Hybrid'),
    ]

    EXPERIENCE_LEVEL_CHOICES = [
        ('entry', 'Entry'),
        ('mid', 'Mid'),
        ('senior', 'Senior'),
        ('executive', 'Executive'),
        ('manager', 'Manager'),
    ]

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=250, unique=True, blank=True)
    company = models.ForeignKey(CompanyProfile, on_delete=models.CASCADE, related_name="jobs")
    location = models.CharField(max_length=200)
    description = RichTextField()
    
    categories = models.ManyToManyField("Category", related_name="jobs")

    created_at = models.DateTimeField(auto_now_add=True)

    internal_or_external = models.CharField(max_length=10, choices=JOB_TYPE, default='internal')
    external_url = models.URLField(blank=True, null=True)
    external_company_name = models.CharField(blank=True, max_length=255)

    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, blank=True, null=True)

    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVEL_CHOICES, blank=True, null=True)

    salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    views = models.PositiveIntegerField(default=0)

    class Meta:
        ordering = ['-created_at']
        indexes = [models.Index(fields=['slug'])]

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(f"{self.title}-{self.company.company_name}")
        super().save(*args, **kwargs)

    def clean(self):
        if self.internal_or_external == 'external' and not self.external_url:
            raise ValidationError("External jobs must include an external URL.")

    def __str__(self):
        return f"{self.title} at {self.company.company_name}"

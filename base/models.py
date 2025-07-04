import os
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.core.exceptions import ValidationError
from django.utils.text import slugify
from django.conf import settings
from ckeditor.fields import RichTextField
from PyPDF2 import PdfReader, PdfWriter
from io import BytesIO
from django.core.files.base import ContentFile

from django.utils import timezone
from django.utils.translation import gettext_lazy as _
from django.db.models import Index

from taggit.managers import TaggableManager

from imagekit.models import ImageSpecField
from imagekit.processors import ResizeToFill

from django.core.validators import FileExtensionValidator

from datetime import timedelta



class CompanyProfile(models.Model):
    company_name = models.CharField(max_length=255)
    website = models.URLField(blank=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.company_name


class User(AbstractUser):

    USER_TYPE_CHOICES = (
        ('admin', 'Admin'),
        ('candidate', 'Candidate'),
        ('employer', 'Employer'),
    )
    user_type = models.CharField(max_length=20, choices=USER_TYPE_CHOICES, default='candidate')

    def is_candidate(self):
        return self.user_type == 'candidate'

    def is_admin_user(self):
        return self.user_type == 'admin'

    is_company = models.BooleanField(default=False)
    company = models.ForeignKey(CompanyProfile, on_delete=models.SET_NULL, null=True, blank=True, related_name='users')

    def __str__(self):
        return self.username





class Category(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class SubCategory(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True, blank=True)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, related_name='subcategories')

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.category.name})"



class JobNotificationSub(models.Model):
    subscribe_email = models.CharField(max_length=255)
    notification_count = models.PositiveIntegerField(default=0)



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

    categories = models.ManyToManyField(Category, related_name="jobs")
    subcategories = models.ManyToManyField(SubCategory, related_name="jobs", blank=True)

    created_at = models.DateTimeField(auto_now_add=True)

    internal_or_external = models.CharField(max_length=10, choices=JOB_TYPE, default='internal')
    external_url = models.URLField(blank=True, null=True)
    external_company_name = models.CharField(blank=True, max_length=255)

    job_type = models.CharField(max_length=20, choices=JOB_TYPE_CHOICES, blank=True, null=True)

    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVEL_CHOICES, blank=True, null=True)

    salary = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    views = models.PositiveIntegerField(default=0)
    deadline = models.DateField(default=timezone.now() + timedelta(days=180))

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
    

class SalaryRequest(models.Model):
    job_title = models.CharField(max_length=255, unique=True, null=True)
    location = models.CharField(max_length=255, blank=True)
    requests_count = models.PositiveIntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.job_title} ({self.requests_count} requests)"



class SalaryCompany(models.Model):
    name = models.CharField(max_length=255)

    def __str__(self):
        return self.name

class SalaryReport(models.Model):
    SALARY_TYPE_CHOICES = [
        ('yearly', 'Per Year'),
        ('monthly', 'Per Month'),
        ('daily', 'Per Day'),
        ('hourly', 'Per Hour'),
    ]

    title = models.CharField(max_length=255)  # e.g., "Front-End Developer"
    slug = models.SlugField(max_length=255, unique=True, blank=True)

    location = models.CharField(max_length=255, blank=True, null=True)
     

    categories = models.ManyToManyField("Category", related_name="salary_reports", blank=True)
    companies = models.ManyToManyField("SalaryCompany", related_name="salary_reports", blank=True)

    low_salary = models.DecimalField(max_digits=10, decimal_places=2)
    average_salary = models.DecimalField(max_digits=10, decimal_places=2)
    high_salary = models.DecimalField(max_digits=10, decimal_places=2)
    salary_type = models.CharField(max_length=20, choices=SALARY_TYPE_CHOICES, default='yearly')

    overview = RichTextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} Salary Report"
    
    def save(self, *args, **kwargs):
        if not self.slug:
            base_slug = slugify(self.title)
            slug = base_slug
            counter = 1
            while SalaryReport.objects.filter(slug=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.slug = slug
        super().save(*args, **kwargs)


class Subject(models.Model):
    name = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(max_length=120, unique=True, blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class PastPaper(models.Model):
    PAPER_NUMBER_CHOICES = [
        ('Paper 1', 'Paper 1'),
        ('Paper 2', 'Paper 2'),
        ('Paper 3', 'Paper 3'),
    ]

    GRADE_CHOICES = [
        ('Grade 10', 'Grade 10'),
        ('Grade 11', 'Grade 11'),
        ('Grade 12', 'Grade 12'),
    ]

    subject = models.ForeignKey(Subject, on_delete=models.CASCADE, related_name="papers")
    paper_number = models.CharField(max_length=20, choices=PAPER_NUMBER_CHOICES)
    grade = models.CharField(max_length=20, choices=GRADE_CHOICES)
    exam_month = models.CharField(max_length=20)  # e.g., "November"
    exam_year = models.PositiveIntegerField()     # e.g., 2023

    file = models.FileField(upload_to='past_papers/questions/')
    memo = models.FileField(upload_to='past_papers/memos/')
    created_at = models.DateTimeField(auto_now_add=True)
    download_count = models.PositiveIntegerField(default=0) 

    class Meta:
        ordering = ['-exam_year', 'subject']

    def apply_watermark(self, file_field):
        if file_field and file_field.name.endswith('.pdf'):
            original_path = file_field.path
            watermark_path = os.path.join('media', 'watermark.pdf')

            try:
                input_pdf = PdfReader(original_path)
                watermark = PdfReader(watermark_path)
                watermark_page = watermark.pages[0]
            except Exception as e:
                print(f"Watermarking failed: {e}")
                return

            output_pdf = PdfWriter()
            for page in input_pdf.pages:
                page.merge_page(watermark_page)
                output_pdf.add_page(page)

            output_stream = BytesIO()
            output_pdf.write(output_stream)

            # Clean filename and re-assign to same folder
            base_name = os.path.basename(file_field.name)
            file_field.delete(save=False)  # Delete unwatermarked file
            file_field.save(base_name, ContentFile(output_stream.getvalue()), save=False)
            output_stream.close()

    def save(self, *args, **kwargs):
        is_new = self.pk is None
        super().save(*args, **kwargs)

        if is_new:
            self.apply_watermark(self.file)
            self.apply_watermark(self.memo)
            super().save(update_fields=['file', 'memo'])

    def __str__(self):
        return f"{self.subject.name} {self.paper_number} – {self.exam_month} {self.exam_year}"


#  ARTICLE MODELS 


class ArticleCategory(models.Model):
    name = models.CharField(
        max_length=100,
        unique=True,
        verbose_name=_("Name"),
        help_text=_("Category name (max 100 characters)")
    )
    slug = models.SlugField(
        max_length=120,
        unique=True,
        blank=True,
        verbose_name=_("Slug"),
        help_text=_("URL-friendly identifier (auto-generated if blank)")
    )

    class Meta:
        verbose_name = _("Article Category")
        verbose_name_plural = _("Article Categories")
        ordering = ['name']
        indexes = [
            Index(fields=['name']),
            Index(fields=['slug']),
        ]

    def __str__(self):
        return self.name

    def clean(self):
        if not self.slug:
            self.slug = slugify(self.name)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


def article_cover_upload_path(instance, filename):
    return f'articles/images/{instance.slug}/{filename}'


class Article(models.Model):
    STATUS_DRAFT = 'draft'
    STATUS_PUBLISHED = 'published'
    STATUS_ARCHIVED = 'archived'
    
    STATUS_CHOICES = [
        (STATUS_DRAFT, _('Draft')),
        (STATUS_PUBLISHED, _('Published')),
        (STATUS_ARCHIVED, _('Archived')),
    ]

    title = models.CharField(
        max_length=200,
        verbose_name=_("Title"),
        help_text=_("Article title (max 200 characters)")
    )
    slug = models.SlugField(
        max_length=220,
        unique=True,
        blank=True,
        verbose_name=_("Slug"),
        help_text=_("URL-friendly identifier (auto-generated if blank)")
    )
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        related_name='articles',
        verbose_name=_("Author")
    )
    category = models.ForeignKey(
        ArticleCategory,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='articles',
        verbose_name=_("Category")
    )
    cover_image = models.ImageField(
        upload_to=article_cover_upload_path,
        blank=True,
        null=True,
        verbose_name=_("Cover Image"),
        help_text=_("Recommended size: 1200x630 pixels")
    )
    cover_image_thumbnail = ImageSpecField(
        source='cover_image',
        processors=[ResizeToFill(400, 300)],
        format='JPEG',
        options={'quality': 80}
    )

    content = RichTextField(
        verbose_name=_("Content"),
        help_text=_("Main article content")
    )
    excerpt = models.TextField(
        max_length=300,
        blank=True,
        verbose_name=_("Excerpt"),
        help_text=_("Short summary for previews (max 300 characters)")
    )

    tags = TaggableManager(
        blank=True,
        verbose_name=_("Tags"),
        help_text=_("Comma-separated tags for this article")
    )

    status = models.CharField(
        max_length=10,
        choices=STATUS_CHOICES,
        default=STATUS_DRAFT,
        verbose_name=_("Status"),
        help_text=_("Publication status")
    )
    is_featured = models.BooleanField(
        default=False,
        verbose_name=_("Featured"),
        help_text=_("Mark as featured article")
    )

    published_at = models.DateTimeField(
        blank=True,
        null=True,
        verbose_name=_("Published At"),
        help_text=_("Date when article was published")
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name=_("Created At")
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name=_("Updated At")
    )
    view_count = models.PositiveIntegerField(
        default=0,
        editable=False,
        verbose_name=_("View Count")
    )

    # SEO Fields
    meta_title = models.CharField(
        max_length=70,
        blank=True,
        verbose_name=_("Meta Title"),
        help_text=_("SEO title (max 70 characters)")
    )
    meta_description = models.CharField(
        max_length=160,
        blank=True,
        verbose_name=_("Meta Description"),
        help_text=_("SEO description (max 160 characters)")
    )

    class Meta:
        ordering = ['-published_at', '-created_at']
        verbose_name = _("Article")
        verbose_name_plural = _("Articles")
        indexes = [
            Index(fields=['status']),
            Index(fields=['published_at']),
            Index(fields=['is_featured']),
            Index(fields=['slug']),
        ]

    def __str__(self):
        return self.title

    def clean(self):
        # Auto-generate slug if empty
        if not self.slug:
            base_slug = slugify(self.title)[:220]
            unique_slug = base_slug
            counter = 1
            while Article.objects.filter(slug=unique_slug).exclude(pk=self.pk).exists():
                unique_slug = f'{base_slug}-{counter}'
                counter += 1
            self.slug = unique_slug

        # Set published_at when status changes to published
        if self.status == self.STATUS_PUBLISHED and not self.published_at:
            self.published_at = timezone.now()

        # Validate published_at isn't in the future
        if self.published_at and self.published_at > timezone.now():
            raise ValidationError(_("Published date cannot be in the future"))

        # Set meta_title if empty
        if not self.meta_title:
            self.meta_title = self.title[:70]

        # Set meta_description if empty
        if not self.meta_description and self.excerpt:
            self.meta_description = self.excerpt[:160]

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)

    def is_published(self):
        return self.status == self.STATUS_PUBLISHED

    def get_reading_time(self):
        """Estimate reading time in minutes (average 200 words per minute)"""
        word_count = len(self.content.split())
        return max(1, word_count // 200)

    def increment_view_count(self):
        """Atomically increment view count"""
        Article.objects.filter(pk=self.pk).update(
            view_count=models.F('view_count') + 1
        )
        self.refresh_from_db()



class Certification(models.Model):
    TITLE_CHOICES = [
        ('FREE', 'Free'),
        ('PAID', 'Paid'),
    ]

    title = models.CharField(max_length=255)
    provider = models.CharField(max_length=255, blank=True)  # e.g., Coursera, Google, etc.
    description = models.TextField()
    link = models.URLField(verbose_name="External Link")
    image = models.ImageField(upload_to='certifications/', blank=True, null=True)
    price_type = models.CharField(max_length=10, choices=TITLE_CHOICES, default='FREE')
    price = models.DecimalField(max_digits=8, decimal_places=2, default=0.00)
    students_enrolled = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return self.title




class Bursary(models.Model):
    title = models.CharField(
        max_length=200,
        unique=True,
        verbose_name="Bursary Title",
        help_text="Enter the official name of the bursary or funding opportunity."
    )
    slug = models.SlugField(
        max_length=220,
        unique=True,
        blank=True,
        help_text="Auto-generated from the title"
    )
    provider = models.CharField(
        max_length=150,
        verbose_name="Provider",
        help_text="Organization or institution offering this bursary"
    )
    description = models.TextField(
        verbose_name="Description",
        help_text="Brief details about the bursary or funding"
    )
    eligibility = models.TextField(
        blank=True,
        verbose_name="Eligibility Requirements",
        help_text="Who can apply for this bursary"
    )
    deadline = models.DateField(
        blank=True,
        null=True,
        verbose_name="Application Deadline"
    )
    website_link = models.URLField(
        blank=True,
        null=True,
        verbose_name="Provider Website Link",
        help_text="Official website or application page"
    )
    application_pdf = models.FileField(
        upload_to='bursaries/pdfs/',
        blank=True,
        null=True,
        verbose_name="Downloadable PDF",
        validators=[FileExtensionValidator(['pdf'])],
        help_text="Optional brochure or application form in PDF format"
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        verbose_name = "Bursary or Funding Opportunity"
        verbose_name_plural = "Bursaries & Funding"
        ordering = ['-deadline', 'title']

    def __str__(self):
        return self.title

    def clean(self):
        # Enforce at least a website or a PDF
        if not self.website_link and not self.application_pdf:
            raise ValidationError("You must provide at least a PDF or a website link.")
        if self.deadline and self.deadline < timezone.now().date():
            raise ValidationError("The deadline cannot be in the past.")
        if not self.slug:
            self.slug = slugify(self.title)

    def save(self, *args, **kwargs):
        self.full_clean()
        super().save(*args, **kwargs)


class ContactMessage(models.Model):
    name = models.CharField(max_length=100)
    email = models.EmailField()
    subject = models.CharField(max_length=200)
    message = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Message from {self.name} - {self.subject}"
    


class University(models.Model):
    name = models.CharField(max_length=255, unique=True)
    acronym = models.CharField(max_length=20, blank=True, help_text="e.g., TUT, UJ, UCT")
    slug = models.SlugField(max_length=255, unique=True, blank=True)
    logo = models.ImageField(upload_to='university_logos/', blank=True, null=True)

    website = models.URLField(blank=True)
    description = models.TextField(blank=True)

    class Meta:
        verbose_name = _("University")
        verbose_name_plural = _("Universities")
        ordering = ['name']

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

class Prospectus(models.Model):
    university = models.ForeignKey(University, on_delete=models.CASCADE, related_name='prospectuses')
    title = models.CharField(max_length=255, help_text="e.g. 2025 Undergraduate Prospectus")
    year = models.PositiveIntegerField()
    file = models.FileField(
        upload_to='prospectuses/',
        validators=[FileExtensionValidator(allowed_extensions=['pdf'])],
        help_text="Upload PDF format only"
    )

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = _("Prospectus")
        verbose_name_plural = _("Prospectuses")
        ordering = ['-year', 'university']

    def __str__(self):
        return f"{self.university.name} - {self.title}"
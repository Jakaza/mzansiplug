from django.db import models
from django.contrib.auth.models import AbstractUser
from django.utils.text import slugify

# Create your models here.

# USER 

class User(AbstractUser):
    USER_TYPES = (
        ('job_seeker', 'Job Seeker'),
        ('employer', 'Employer'),
        ('admin', 'Admin'),
    )
    
    user_type = models.CharField(max_length=20, choices=USER_TYPES)
    phone = models.CharField(max_length=20, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    is_verified = models.BooleanField(default=False)
    verification_token = models.CharField(max_length=255, blank=True, null=True)
    last_login = models.DateTimeField(blank=True, null=True)
    
    # Author fields
    is_author = models.BooleanField(default=False)
    author_bio = models.TextField(blank=True, null=True)
    author_profile_picture = models.ImageField(upload_to='author_pics/', blank=True, null=True)
    author_social_links = models.JSONField(blank=True, null=True)

class JobSeekerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='job_seeker_profile')
    headline = models.CharField(max_length=255, blank=True, null=True)
    bio = models.TextField(blank=True, null=True)
    location_city = models.CharField(max_length=100, blank=True, null=True)
    location_province = models.CharField(max_length=100, blank=True, null=True)
    willing_to_relocate = models.BooleanField(default=False)
    resume = models.FileField(upload_to='resumes/', blank=True, null=True)
    cover_letter = models.FileField(upload_to='cover_letters/', blank=True, null=True)

class EmployerProfile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='employer_profile')
    company_name = models.CharField(max_length=255)
    company_description = models.TextField(blank=True, null=True)
    industry = models.CharField(max_length=100, blank=True, null=True)
    website_url = models.URLField(blank=True, null=True)
    logo = models.ImageField(upload_to='company_logos/', blank=True, null=True)
    
    COMPANY_SIZES = (
        ('1-10', '1-10 employees'),
        ('11-50', '11-50 employees'),
        ('51-200', '51-200 employees'),
        ('201-500', '201-500 employees'),
        ('501-1000', '501-1000 employees'),
        ('1000+', '1000+ employees'),
    )
    
    company_size = models.CharField(max_length=20, choices=COMPANY_SIZES, blank=True, null=True)
    founded_year = models.IntegerField(blank=True, null=True)



# JOBS MODEL

class JobCategory(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True, null=True)
    parent_category = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True)

    def __str__(self):
        return self.name

class Job(models.Model):
    JOB_TYPES = (
        ('full_time', 'Full Time'),
        ('part_time', 'Part Time'),
        ('contract', 'Contract'),
        ('internship', 'Internship'),
        ('temporary', 'Temporary'),
        ('remote', 'Remote'),
        ('hybrid', 'Hybrid'),
        ('permanent', 'Permanent'),
        ('project_based', 'Project Based'),
    )
    
    EXPERIENCE_LEVELS = (
        ('entry', 'Entry Level'),
        ('mid', 'Mid Level'),
        ('senior', 'Senior Level'),
        ('executive', 'Executive'),
        ('manager', 'Manager'),
    )
    
    employer = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_jobs')
    title = models.CharField(max_length=255)
    description = models.TextField()
    requirements = models.TextField(blank=True, null=True)
    responsibilities = models.TextField(blank=True, null=True)
    job_type = models.CharField(max_length=20, choices=JOB_TYPES)
    experience_level = models.CharField(max_length=20, choices=EXPERIENCE_LEVELS)
    location_city = models.CharField(max_length=100, blank=True, null=True)
    location_province = models.CharField(max_length=100, blank=True, null=True)
    is_remote = models.BooleanField(default=False)
    salary_min = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    salary_max = models.DecimalField(max_digits=12, decimal_places=2, blank=True, null=True)
    salary_currency = models.CharField(max_length=3, default='ZAR')
    salary_is_public = models.BooleanField(default=True)
    application_deadline = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views_count = models.IntegerField(default=0)
    categories = models.ManyToManyField(JobCategory, related_name='jobs')

    def __str__(self):
        return f"{self.title} at {self.employer.employer_profile.company_name}"

class Application(models.Model):
    STATUS_CHOICES = (
        ('submitted', 'Submitted'),
        ('reviewed', 'Reviewed'),
        ('interviewing', 'Interviewing'),
        ('offered', 'Offered'),
        ('rejected', 'Rejected'),
        ('hired', 'Hired'),
    )
    
    job = models.ForeignKey(Job, on_delete=models.CASCADE, related_name='applications')
    applicant = models.ForeignKey(User, on_delete=models.CASCADE, related_name='job_applications')
    cover_letter = models.TextField(blank=True, null=True)
    resume = models.FileField(upload_to='application_resumes/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='submitted')
    applied_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = ('job', 'applicant')


# Opportunities MODEL


class Opportunity(models.Model):
    OPPORTUNITY_TYPES = (
        ('learnership', 'Learnership'),
        ('internship', 'Internship'),
        ('bursary', 'Bursary'),
        ('scholarship', 'Scholarship'),
        ('volunteer', 'Volunteer Work'),
        ('side_hustle', 'Side Hustle'),
        ('entrepreneurial', 'Entrepreneurial Opportunity'),
    )
    
    poster = models.ForeignKey(User, on_delete=models.CASCADE, related_name='posted_opportunities')
    title = models.CharField(max_length=255)
    description = models.TextField()
    type = models.CharField(max_length=20, choices=OPPORTUNITY_TYPES)
    location_city = models.CharField(max_length=100, blank=True, null=True)
    location_province = models.CharField(max_length=100, blank=True, null=True)
    is_remote = models.BooleanField(default=False)
    deadline = models.DateField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    views_count = models.IntegerField(default=0)
    application_url = models.URLField(blank=True, null=True)

    def __str__(self):
        return self.title
    

# Articles MODEL

class ArticleCategory(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(max_length=100, unique=True)
    description = models.TextField(blank=True, null=True)
    parent_category = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class ArticleTag(models.Model):
    name = models.CharField(max_length=50)
    slug = models.SlugField(max_length=50, unique=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name

class Article(models.Model):
    STATUS_CHOICES = (
        ('draft', 'Draft'),
        ('published', 'Published'),
        ('archived', 'Archived'),
    )
    
    author = models.ForeignKey(User, on_delete=models.CASCADE, related_name='articles')
    title = models.CharField(max_length=255)
    slug = models.SlugField(max_length=255, unique=True)
    excerpt = models.TextField(blank=True, null=True)
    content = models.TextField()
    featured_image = models.ImageField(upload_to='article_images/', blank=True, null=True)
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    published_at = models.DateTimeField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    views_count = models.IntegerField(default=0)
    is_featured = models.BooleanField(default=False)
    reading_time_minutes = models.IntegerField(blank=True, null=True)
    meta_title = models.CharField(max_length=255, blank=True, null=True)
    meta_description = models.TextField(blank=True, null=True)
    categories = models.ManyToManyField(ArticleCategory, related_name='articles')
    tags = models.ManyToManyField(ArticleTag, related_name='articles', blank=True)

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

class ArticleComment(models.Model):
    article = models.ForeignKey(Article, on_delete=models.CASCADE, related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='article_comments')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    parent_comment = models.ForeignKey('self', on_delete=models.SET_NULL, blank=True, null=True)
    is_approved = models.BooleanField(default=True)

    def __str__(self):
        return f"Comment by {self.user.username} on {self.article.title}"
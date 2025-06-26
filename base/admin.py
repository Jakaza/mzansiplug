from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (User, CompanyProfile, Category, Job, SalaryReport, 
                    SalaryCompany, SalaryRequest, Article, ArticleCategory,
                    University , Prospectus,
                    JobNotificationSub, Subject, PastPaper , Bursary, Certification  , ContactMessage, SubCategory)
from django.utils.html import format_html
from .forms import JobAdminForm
from django import forms
from django.db.models import Count
from taggit.models import Tag  # Added the missing import


from django.urls import path
from django.template.response import TemplateResponse
from django.db.models import Count, Sum
from django.utils.timezone import now, timedelta


# Register your models here.

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User

@admin.register(PastPaper)
class PastPaperAdmin(admin.ModelAdmin):
    list_display = ('subject', 'paper_number', 'grade', 'exam_month', 'exam_year', 'file')

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'user', 'logo_preview')
    readonly_fields = ('logo_preview',)

    def logo_preview(self, obj):
        if obj.logo:
            return format_html('<img src="{}" width="100" height="100" style="object-fit: contain;" />', obj.logo.url)
        return "No logo"
    logo_preview.short_description = 'Logo Preview'

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}


@admin.register(SubCategory)
class SubCategoryAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}



@admin.register(ContactMessage)
class ContactMessageAdmin(admin.ModelAdmin):
    list_display = ("name", "email", "subject", "created_at")

@admin.register(JobNotificationSub)
class JobNotificationSubAdmin(admin.ModelAdmin):
    list_display = ("subscribe_email", "notification_count")

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    form = JobAdminForm
    prepopulated_fields = {"slug": ("title",)}
    list_display = ("title", "company", "location", "internal_or_external", "created_at", "deadline")
    list_filter = ("categories", "internal_or_external", "job_type", "experience_level")

@admin.register(SalaryCompany)
class SalaryCompanyAdmin(admin.ModelAdmin):
    search_fields = ['name']

@admin.register(SalaryReport)
class SalaryReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'average_salary', 'salary_type', 'created_at')
    list_filter = ('salary_type', 'categories')
    search_fields = ('title', 'location')
    filter_horizontal = ('categories', 'companies')

@admin.register(SalaryRequest)
class SalaryRequestAdmin(admin.ModelAdmin):
    list_display = ('job_title', 'location', 'requests_count', 'created_at')
    search_fields = ('job_title', 'location')
    list_filter = ('created_at',)

@admin.register(ArticleCategory)
class ArticleCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug', 'pk' , 'article_count')
    prepopulated_fields = {'slug': ('name',)}
    
    def get_queryset(self, request):
        queryset = super().get_queryset(request)
        queryset = queryset.annotate(_article_count=Count('articles'))
        return queryset
    
    def article_count(self, obj):
        return obj._article_count
    article_count.admin_order_field = '_article_count'

class TagifyWidget(forms.TextInput):
    class Media:
        css = {
            'all': ('https://cdn.jsdelivr.net/npm/@yaireo/tagify/dist/tagify.css',)
        }
        js = (
            'https://cdn.jsdelivr.net/npm/@yaireo/tagify', 
            'js/admin_tagify_init.js',
        )

    def __init__(self, attrs=None):
        default_attrs = {
            'placeholder': 'Add tags, separate with commas',
            'data-blacklist': '{,},[,],:,",\'',  # Prevent these characters
        }
        if attrs:
            default_attrs.update(attrs)
        super().__init__(default_attrs)

    def format_value(self, value):
        """Convert queryset or list of tags to comma-separated string"""
        if isinstance(value, str):
            return value
        elif hasattr(value, 'all'):
            return ", ".join(tag.name for tag in value.all())
        elif isinstance(value, (list, tuple)):
            return ", ".join(str(v) for v in value)
        return super().format_value(value)


class ArticleAdminForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = '__all__'
        widgets = {
            'tags': TagifyWidget(),
        }

    def clean_tags(self):
        tag_str = self.cleaned_data.get('tags')
        if isinstance(tag_str, str):
            tag_list = [tag.strip() for tag in tag_str.split(',') if tag.strip()]
            return tag_list
        return tag_str

@admin.register(Article)
class ArticleAdmin(admin.ModelAdmin):
    form = ArticleAdminForm
    list_display = ('title', 'author', 'status', 'published_at', 'view_count', 'display_tags')
    list_filter = ('status', 'published_at', 'is_featured', 'category')
    search_fields = ('title', 'content', 'author__username', 'tags__name')
    prepopulated_fields = {"slug": ("title",)}
    ordering = ('-published_at',)
    actions = ['clean_article_tags']
    readonly_fields = ('view_count',)
    filter_horizontal = ()

    def display_tags(self, obj):
        valid_tags = obj.tags.filter(name__regex=r'^[^{}\[\]:"\']+$')
        return ", ".join(tag.name for tag in valid_tags)
    display_tags.short_description = 'Tags'

    def clean_article_tags(self, request, queryset):
        cleaned_count = 0
        for article in queryset:
            # Get valid tags using regex to filter out invalid ones
            valid_tags = list(article.tags.filter(name__regex=r'^[^{}\[\]:"\']+$'))
            
            # Clear and reset only valid tags
            article.tags.clear()
            article.tags.add(*[tag.name for tag in valid_tags])
            cleaned_count += 1
            
        self.message_user(
            request, 
            f"Successfully cleaned tags for {cleaned_count} articles."
        )
    clean_article_tags.short_description = "Clean invalid tags from selected articles"

    def get_queryset(self, request):
        return super().get_queryset(request).prefetch_related('tags')
    


@admin.register(Bursary)
class BursaryAdmin(admin.ModelAdmin):
    list_display = ('title', 'provider', 'deadline', 'created_at')
    search_fields = ('title', 'provider', 'description')
    prepopulated_fields = {"slug": ("title",)}
    list_filter = ('deadline', 'provider')


@admin.register(Certification)
class CertificationAdmin(admin.ModelAdmin):
    list_display = ('title', 'provider', 'price_type', 'students_enrolled', 'created_at')
    search_fields = ('title', 'provider')
    list_filter = ('price_type',)


@admin.register(University)
class UniversityAdmin(admin.ModelAdmin):
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Prospectus)
class ProspectusAdmin(admin.ModelAdmin):
    list_display = ('university', 'title', 'year', 'created_at')
    list_filter = ('university', 'year')
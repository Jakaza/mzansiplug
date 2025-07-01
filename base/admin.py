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


admin.site.site_header = "MzansiPlug Admin"
admin.site.site_title = "MzansiPlug Portal"
admin.site.index_title = "Welcome to MzansiPlug Admin Dashboard"


# Register your models here.

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User

    list_display = ('username', 'email', 'is_staff', 'is_company', 'company')
    list_filter = ('is_company', 'company')

    fieldsets = BaseUserAdmin.fieldsets + (
        ('Company Info', {'fields': ('is_company', 'company')}),
    )

    add_fieldsets = BaseUserAdmin.add_fieldsets + (
        ('Company Info', {'fields': ('is_company', 'company')}),
    )

    search_fields = ('username', 'email', 'company__company_name')

@admin.register(PastPaper)
class PastPaperAdmin(admin.ModelAdmin):
    list_display = ('subject', 'paper_number', 'grade', 'exam_month', 'exam_year', 'file')

@admin.register(Subject)
class SubjectAdmin(admin.ModelAdmin):
    list_display = ('name', 'slug')
    prepopulated_fields = {'slug': ('name',)}

class UserInline(admin.TabularInline):
    model = User
    fields = ('username', 'email', 'is_staff', 'is_company')
    extra = 1
    show_change_link = True

@admin.register(CompanyProfile)
class CompanyProfileAdmin(admin.ModelAdmin):
    list_display = ('company_name', 'user_count', 'logo_preview')
    readonly_fields = ('logo_preview',)
    inlines = [UserInline]

    def user_count(self, obj):
        return obj.users.count()
    user_count.short_description = 'Users'

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


from django.core.exceptions import ValidationError

class ArticleAdminForm(forms.ModelForm):
    class Meta:
        model = Article
        fields = '__all__'
        widgets = {
            'tags': TagifyWidget(),
        }

    def clean_title(self):
        title = self.cleaned_data.get('title', '')
        if len(title) > 200:
            raise ValidationError('Title cannot exceed 200 characters.')
        return title

    def clean_excerpt(self):
        excerpt = self.cleaned_data.get('excerpt', '')
        if len(excerpt) > 300:
            raise ValidationError('Excerpt cannot exceed 300 characters.')
        return excerpt

    def clean_meta_title(self):
        meta_title = self.cleaned_data.get('meta_title', '')
        if len(meta_title) > 70:
            raise ValidationError('Meta Title cannot exceed 70 characters.')
        return meta_title

    def clean_meta_description(self):
        meta_description = self.cleaned_data.get('meta_description', '')
        if len(meta_description) > 160:
            raise ValidationError('Meta Description cannot exceed 160 characters.')
        return meta_description

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Add help text showing max length, no live count but at least users know the limit
        self.fields['title'].help_text = "Max 200 characters"
        self.fields['excerpt'].help_text = "Max 300 characters"
        self.fields['meta_title'].help_text = "Max 70 characters"
        self.fields['meta_description'].help_text = "Max 160 characters"
   

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
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (User, CompanyProfile , Category , Job , SalaryReport , SalaryCompany , SalaryRequest , JobNotificationSub , Subject , PastPaper)
from django.utils.html import format_html
from .forms import JobAdminForm

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
   pass


@admin.register(JobNotificationSub)
class JobNotificationSubAdmin(admin.ModelAdmin):
   list_display = ("subscribe_email" , "notification_count")


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
 form = JobAdminForm
 prepopulated_fields = {"slug": ("title",)}
 list_display = ("title", "company", "location", "internal_or_external", "created_at")


@admin.register(SalaryCompany)
class SalaryCompanyAdmin(admin.ModelAdmin):
    search_fields = ['name']

    
@admin.register(SalaryReport)
class SalaryReportAdmin(admin.ModelAdmin):
    list_display = ('title', 'location', 'average_salary', 'salary_type', 'created_at')
    list_filter = ('salary_type', 'categories')
    search_fields = ('title', 'location')
    filter_horizontal = ('categories', 'companies')  # Better UI for multi-select


@admin.register(SalaryRequest)
class SalaryRequestAdmin(admin.ModelAdmin):
    list_display = ('job_title', 'location', 'requests_count', 'created_at')
    search_fields = ('job_title', 'location')
    list_filter = ('created_at',)



from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import (User, CompanyProfile , Category , Job)
from django.utils.html import format_html
from .forms import JobAdminForm

# Register your models here.

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User


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


@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
 form = JobAdminForm
 prepopulated_fields = {"slug": ("title",)}
 list_display = ("title", "company", "location", "internal_or_external", "created_at")
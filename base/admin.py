from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.contrib.auth.models import Group
from .models import User, EmployerProfile, JobSeekerProfile
from .models import JobCategory, Job, Application


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    model = User
    list_display = ('username', 'email', 'is_staff', 'is_active')
    list_filter = ('is_staff', 'is_active', 'groups')
    search_fields = ('username', 'email')
    ordering = ('username',)

    fieldsets = (
        (None, {'fields': ('username', 'email', 'password')}),
        ('Personal Info', {'fields': ('first_name', 'last_name', 'profile_picture', 'author_profile_picture')}),
        ('Permissions', {'fields': ('is_active', 'is_staff', 'is_superuser', 'groups', 'user_permissions')}),
        ('Important Dates', {'fields': ('last_login', 'date_joined')}),
    )

    add_fieldsets = (
        (None, {
            'classes': ('wide',),
            'fields': ('username', 'email', 'password1', 'password2', 'is_staff', 'is_active')}
        ),
    )

@admin.register(EmployerProfile)
class EmployerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'company_name')

@admin.register(JobSeekerProfile)
class JobSeekerProfileAdmin(admin.ModelAdmin):
    list_display = ('user', 'bio')


# Job 

@admin.register(JobCategory)
class JobCategoryAdmin(admin.ModelAdmin):
    list_display = ('name', 'parent_category')
    search_fields = ('name',)
    list_filter = ('parent_category',)

@admin.register(Job)
class JobAdmin(admin.ModelAdmin):
    list_display = ('title', 'employer', 'job_type', 'experience_level', 'is_active', 'created_at')
    list_filter = ('job_type', 'experience_level', 'is_active', 'application_deadline', 'categories')
    search_fields = ('title', 'employer__username', 'location_city', 'location_province')
    filter_horizontal = ('categories',)
    readonly_fields = ('views_count', 'created_at', 'updated_at')

@admin.register(Application)
class ApplicationAdmin(admin.ModelAdmin):
    list_display = ('job', 'applicant', 'status', 'applied_at')
    list_filter = ('status', 'applied_at', 'job')
    search_fields = ('applicant__username', 'job__title')
    readonly_fields = ('applied_at', 'updated_at')

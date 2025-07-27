from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone
from django.conf import settings
import uuid


class CustomUser(AbstractUser):
    """
    Custom User model extending Django's AbstractUser
    """
    email = models.EmailField(unique=True)
    first_name = models.CharField(max_length=30)
    last_name = models.CharField(max_length=30)
    is_verified = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    last_login = models.DateTimeField(null=True, blank=True)
    
    # Additional fields for user profile
    phone_number = models.CharField(max_length=15, blank=True, null=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    bio = models.TextField(max_length=500, blank=True, null=True)
    profile_picture = models.ImageField(upload_to='profile_pics/', blank=True, null=True)
    
    # Email as username
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name']
    
    class Meta:
        db_table = 'auth_user'
        verbose_name = 'User'
        verbose_name_plural = 'Users'
        
    def __str__(self):
        return f"{self.first_name} {self.last_name} ({self.email})"
    
    def get_full_name(self):
        """Return the first_name plus the last_name, with a space in between."""
        return f"{self.first_name} {self.last_name}".strip()
    
    def get_short_name(self):
        """Return the short name for the user."""
        return self.first_name
    
    @property
    def initials(self):
        """Return user initials for profile picture placeholder"""
        return f"{self.first_name[0]}{self.last_name[0]}".upper() if self.first_name and self.last_name else "U"


class EmailVerificationToken(models.Model):
    """
    Model to store email verification tokens
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    token = models.UUIDField(default=uuid.uuid4, editable=False, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    is_used = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Email Verification Token'
        verbose_name_plural = 'Email Verification Tokens'
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Verification token for {self.user.email}"
    
    def is_expired(self):
        """Check if token is expired (24 hours)"""
        from datetime import timedelta
        return timezone.now() > self.created_at + timedelta(hours=24)
    
    def is_valid(self):
        """Check if token is valid (not used and not expired)"""
        return not self.is_used and not self.is_expired()


class UserLoginHistory(models.Model):
    """
    Track user login history for security purposes
    """
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()
    login_time = models.DateTimeField(auto_now_add=True)
    location = models.CharField(max_length=100, blank=True, null=True)
    device_type = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        verbose_name = 'User Login History'
        verbose_name_plural = 'User Login Histories'
        ordering = ['-login_time']
    
    def __str__(self):
        return f"{self.user.email} - {self.login_time.strftime('%Y-%m-%d %H:%M')}"


class PasswordResetAttempt(models.Model):
    """
    Track password reset attempts for security
    """
    email = models.EmailField()
    ip_address = models.GenericIPAddressField()
    attempted_at = models.DateTimeField(auto_now_add=True)
    success = models.BooleanField(default=False)
    
    class Meta:
        verbose_name = 'Password Reset Attempt'
        verbose_name_plural = 'Password Reset Attempts'
        ordering = ['-attempted_at']
    
    def __str__(self):
        return f"Password reset attempt for {self.email} at {self.attempted_at}"


class UserActivity(models.Model):
    """
    Track user activities on the platform
    """
    ACTIVITY_CHOICES = [
        ('login', 'Login'),
        ('logout', 'Logout'),
        ('profile_update', 'Profile Update'),
        ('password_change', 'Password Change'),
        ('email_verification', 'Email Verification'),
        ('job_application', 'Job Application'),
        ('job_view', 'Job View'),
        ('article_view', 'Article View'),
    ]
    
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    activity_type = models.CharField(max_length=20, choices=ACTIVITY_CHOICES)
    description = models.TextField(blank=True, null=True)
    ip_address = models.GenericIPAddressField(blank=True, null=True)
    timestamp = models.DateTimeField(auto_now_add=True)
    
    # Optional reference to related objects
    object_id = models.PositiveIntegerField(blank=True, null=True)
    object_type = models.CharField(max_length=50, blank=True, null=True)
    
    class Meta:
        verbose_name = 'User Activity'
        verbose_name_plural = 'User Activities'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['user', '-timestamp']),
            models.Index(fields=['activity_type', '-timestamp']),
        ]
    
    def __str__(self):
        return f"{self.user.email} - {self.get_activity_type_display()} at {self.timestamp}"


class UserPreferences(models.Model):
    """
    Store user preferences and settings
    """
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='preferences')
    
    # Email notifications
    email_job_alerts = models.BooleanField(default=True)
    email_newsletter = models.BooleanField(default=True)
    email_marketing = models.BooleanField(default=False)
    
    # Job preferences
    preferred_job_categories = models.JSONField(default=list, blank=True)
    preferred_locations = models.JSONField(default=list, blank=True)
    min_salary = models.PositiveIntegerField(blank=True, null=True)
    max_salary = models.PositiveIntegerField(blank=True, null=True)
    job_type_preferences = models.JSONField(default=list, blank=True)  # full-time, part-time, contract
    
    # Privacy settings
    profile_visibility = models.CharField(
        max_length=10,
        choices=[
            ('public', 'Public'),
            ('private', 'Private'),
            ('limited', 'Limited'),
        ],
        default='public'
    )
    show_email = models.BooleanField(default=False)
    show_phone = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'User Preferences'
        verbose_name_plural = 'User Preferences'
    
    def __str__(self):
        return f"Preferences for {self.user.email}"
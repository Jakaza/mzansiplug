from django.urls import path
from . import views

urlpatterns = [
    path('register/', views.register_candidate, name='register'),
    path('login/', views.login_candidate, name='login'),
    path('logout/', views.logout_candidate, name='logout'),
    path('activate/<uidb64>/<token>/', views.activate_account, name='activate'),
    path('profile/', views.profile_dashboard, name='profile'),
    path('profile-details/', views.profile_details, name='profile-details'),
    path('settings/', views.settings_page, name='settings'),
    path('change-password/', views.change_password, name='change-password'),

    path('profile/update/', views.update_personal_info, name='update-profile'),
    path('profile/education/add/', views.add_education, name='add-education'),
    path('profile/experience/add/', views.add_work_experience, name='add-work-experience'),
    path('profile/skill/add/', views.add_skill, name='add-skill'),
    path('profile/skill/delete/<int:skill_id>/', views.delete_skill, name='delete-skill'),
    path('profile/work/delete/<int:experience_id>/', views.delete_work_experience, name='delete-work-experience'),
    path('profile/education/delete/<int:edu_id>/', views.delete_education, name='delete-education'),
]
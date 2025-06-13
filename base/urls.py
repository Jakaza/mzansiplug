from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    # Jobs
    path('jobs/', views.job_list, name='south-african-jobs'),
    path('jobs/<int:pk>/<slug:slug>/', views.job_detail, name='job-detail'),
    path('jobs/apply/<int:pk>/<slug:slug>/', views.apply_job, name='apply_job'),
    path('job-notification-subscription/' , views.job_notification_subscription , name='job-notification-subscription'),

    # Salaries
    path('salaries/', views.salary_list, name='south-african-salaries'),
    path('salaries/<int:pk>/<slug:slug>/', views.salary_detail, name='salary-detail'),
    path('submit-salary-request/', views.submit_salary_request, name='submit-salary-request'),

    # Careers
    path('careers/', views.career_list, name='south-african-careers'),
    path('careers/highschool', views.highschool, name='highschool'),
    path('careers/past-papers', views.past_papers, name='past-papers'),
    path('download/<int:paper_id>/<str:file_type>/', views.download_paper, name='download-paper'),
    path('careers/graduates-opportunities/', views.graduates_opportunities, name='graduates-opportunities'),
    path('careers/early-career-opportunities/', views.graduates_internships, name='graduates-internships'),

]


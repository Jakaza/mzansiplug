from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),
    # Jobs
    path('jobs/', views.job_list, name='south-african-jobs'),
    path('jobs/<int:pk>/<slug:slug>/', views.job_detail, name='job-detail'),
    path('jobs/apply/<int:pk>/<slug:slug>/', views.apply_job, name='apply_job'),

    # Salaries
    path('salaries/', views.salary_list, name='south-african-salaries'),

    # Careers
    path('careers/', views.career_list, name='south-african-careers'),

]


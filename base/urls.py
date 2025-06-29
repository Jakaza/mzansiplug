from django.urls import path
from . import views

urlpatterns = [
    path('', views.index, name='index'),

    path('robots.txt', views.robots_txt, name='robot'),

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
    path('postgraduate-bursaries/', views.postgraduate_bursaries, name='postgraduate-bursaries'),
    path('undergraduate-bursaries/', views.undergraduate_bursaries, name='undergraduate-bursaries'),
    path('get-certificates/', views.get_certifications, name='get-certificates'),
    path('careers/universities-prospectures/', views.university_prospectus, name='university-prospectus'),


    # Articles 
    path('articles/', views.article_list, name='south-african-articles'),
    path('articles/<int:pk>/<slug:slug>/', views.article_detail, name='article-detail'),
    path('articles/tag/<str:tag_slug>/', views.tagged_articles, name='tagged-articles'),
    path('articles/category/<int:pk>/<str:category_slug>/', views.category_articles, name='category-articles'),


    # Contact 
    path('contact/', views.contact, name='contact'),
    path('about/', views.about, name='about-us'),
    path('privacy-policy/', views.privacy_policy, name='privacy-policy'),
    path('terms-and-conditions/', views.terms_and_conditions, name='terms-and-conditions'),
    path('disclaimer/', views.disclaimer, name='disclaimer'),

]


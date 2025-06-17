from django.shortcuts import render
from django.db.models import Prefetch
from django.db.models import Q
from django.db.models import F
import os
from .models import Job , Category , ArticleCategory , SalaryReport , SalaryCompany , SalaryRequest , Certification , JobNotificationSub , Bursary , Subject , PastPaper , Article
from django.shortcuts import get_object_or_404 , get_list_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.admin.views.decorators import staff_member_required
from django.shortcuts import redirect
from django.contrib import messages
from django.views.decorators.http import require_POST
from django.http import FileResponse
from .models import PastPaper
# import Http404
from django.http import Http404

from taggit.models import Tag  



# Home Views

def index(request):
    category_slug = request.GET.get('category')
    selected_category = None
    if category_slug:
        selected_category = get_object_or_404(Category, slug=category_slug)
        jobs = Job.objects.filter(category=selected_category).order_by('-created_at')[:6]
    else:
        jobs = Job.objects.all().order_by('-created_at')[:6]

    categories = Category.objects.all().order_by('name')

     # Get the most recent job for display in the "featured" section
    latest_job = Job.objects.all().order_by('-created_at').first()
    top_article = Article.objects.filter(status='published').order_by('-view_count').first()
    latest_articles = Article.objects.filter(status='published').order_by('-published_at')[:6]


    return render(request, 'index.html', {
        'categories': categories,
        'jobs': jobs,
        'latest_job': latest_job, 
        'top_article': top_article,
        'selected_category': selected_category,
        'latest_articles': latest_articles,
        'title': 'Welcome to MzansiPlug - South African Jobs and Salaries Platform',

    })


def contact(request):
    return render(request, 'contact.html')



# Jobs Views

def job_list(request):
    # Get query params
    role = request.GET.get('role', '')
    location = request.GET.get('location', '')
    sort = request.GET.get('sort', '')
    job_type = request.GET.get('job_type', '')
    experience_level = request.GET.get('experience_level', '')

    # Base queryset
    jobs = Job.objects.all()

    latest_job = Job.objects.all().order_by('-created_at').first()
    top_article = Article.objects.filter(status='published').order_by('-view_count').first()

    # Filters
    if role:
        jobs = jobs.filter(
            Q(title__icontains=role) |
            Q(description__icontains=role) |
            Q(categories__name__icontains=role)
        ).distinct()
    if location:
        jobs = jobs.filter(location__icontains=location)
    if job_type:
        jobs = jobs.filter(job_type=job_type)
    if experience_level:
        jobs = jobs.filter(experience_level=experience_level)

    # Sorting
    if sort == 'date':
        jobs = jobs.order_by('-created_at')
    elif sort == 'salary_high':
        jobs = jobs.order_by('-salary')
    elif sort == 'salary_low':
        jobs = jobs.order_by('salary')
    elif sort == 'views':
        jobs = jobs.order_by('-views')
    else:
        jobs = jobs.order_by('-created_at')  # default sorting

    context = {
        'jobs': jobs,
        'filters': {
            'role': role,
            'location': location,
            'sort': sort,
            'job_type': job_type,
            'experience_level': experience_level,
        },
        'title': 'South African Jobs available for you to apply',
        'top_article': top_article,
        'latest_job': latest_job, 
    }
    return render(request, 'jobs/job_list.html', context)


def job_detail(request, pk, slug):
    job = get_object_or_404(Job, pk=pk, slug=slug)
    job.views += 1
    job.save()

    current_site = get_current_site(request)
    job_url = request.build_absolute_uri()

    title = f"{job.title} at {job.company.company_name} – {job.location} | Mzansi Plug Jobs"

    return render(request, 'jobs/job-detail.html', {'job': job ,  'job_url': job_url,
        'site': current_site, 'title': title})


def apply_job(request,pk, slug):
    job = get_object_or_404(Job, pk=pk, slug=slug)
    job.views += 1
    job.save()
    title = f"Apply for {job.title} at {job.company.company_name} – {job.location} | Mzansi Plug Jobs"
    return render(request, 'jobs/job-detail.html', {'job': job , 'title': title})

@require_POST
def job_notification_subscription(request):
    if request.method == 'POST':
        subscribe_email = request.POST.get('subscribe-email')

    redirect_url = request.POST.get('next') or '/jobs/'

    if subscribe_email:
        # Check if email already exists
        if not JobNotificationSub.objects.filter(subscribe_email=subscribe_email).exists():
            JobNotificationSub.objects.create(subscribe_email=subscribe_email)
            messages.success(request, "Successfully subscribed to job alerts.")
        else:
            messages.info(request, "You are already subscribed.")
    else:
        messages.error(request, "Invalid email address.")

    return redirect(redirect_url)




# Salaries Views
def submit_salary_request(request):
    if request.method == 'POST':
        job_title = request.POST.get('job_title', '').strip()
        location = request.POST.get('location', '').strip()

        if not job_title:
            messages.error(request, "Job title is required.")
            return redirect(request.META.get('HTTP_REFERER', '/'))

        # Check if a request already exists with the same or similar job title
        existing_request = SalaryRequest.objects.filter(job_title__iexact=job_title).first()

        if existing_request:
            existing_request.requests_count += 1
            existing_request.save()
        else:
            SalaryRequest.objects.create(job_title=job_title, location=location)

        messages.success(request, f"Thanks! We’ll work on getting salary data for '{job_title}' soon.")
        return redirect(request.META.get('HTTP_REFERER', '/'))

    return redirect('/salaries/')



def salary_list(request):
    salaries = SalaryReport.objects.prefetch_related('companies', 'categories').all()

    title_query = request.GET.get('title')
    location_query = request.GET.get('location')
    industry_slug = request.GET.get('industry')

    # Filter by location
    if location_query:
        salaries = salaries.filter(location__icontains=location_query)

    # Filter by industry dropdown (Category slug)
    if industry_slug:
        salaries = salaries.filter(categories__slug=industry_slug)

    # Filter by title/company/category name (typed input)
    if title_query:
        matching_categories = Category.objects.filter(name__icontains=title_query)
        matching_companies = SalaryCompany.objects.filter(name__icontains=title_query)

        salaries = salaries.filter(
            Q(title__icontains=title_query) |
            Q(categories__in=matching_categories) |
            Q(companies__in=matching_companies)
        ).distinct()

    categories = Category.objects.all()

    return render(request, 'salaries/salaries.html', {
        'title': 'Latest Salaries in South Africa – Compare Wages by Industry & Role',
        'salaries': salaries,
        'categories': categories,
    })




def salary_detail(request, pk , slug):
    salary = get_object_or_404(SalaryReport, pk=pk , slug=slug)

    average = salary.average_salary
    low = salary.low_salary
    high = salary.high_salary

    # Calculate percentages for bar widths
    def calc_width(value):
        return round((value / high) * 100) if high else 0
    
    # Get similar salary reports by shared categories, exclude current salary, limit 6
    similar_salaries = SalaryReport.objects.filter(
        categories__in=salary.categories.all()
    ).exclude(pk=salary.pk).distinct()[:6]

    # Related jobs based on shared categories
    related_jobs = Job.objects.filter(
        categories__in=salary.categories.all()
    ).distinct().order_by('-created_at')[:6]

    return render(request, 'salaries/salary-detail.html', {
        'title': f"{salary.title} Salary in South Africa",
        'salary': salary,
        'salary_data': {
            'yearly': average,
            'monthly': round(average / 12, 2),
            'daily': round(average / 260, 2),
            'hourly': round(average / (260 * 8), 2),
        },
        'salary_range': {
            'low': low,
            'average': average,
            'high': high,
            'low_percent': calc_width(low),
            'average_percent': calc_width(average),
            'high_percent': 100,
        },
        'similar_salaries': similar_salaries,
        'related_jobs': related_jobs
    })




# Careers Views 

def career_list(request):


    internship_jobs = Job.objects.filter(
        job_type='internship'
    ).order_by('-created_at')[:6]

    articles = Article.objects.filter(
        status=Article.STATUS_PUBLISHED,
        tags__name__icontains='student'
    ).order_by('-published_at').distinct()[:5]

    return render(request, 'careers/careers.html', {
        'title': 'South African Careers',
        'recommended_articles': articles,
        'internship_jobs': internship_jobs,
    })


def highschool(request):
    recommended_jobs = Job.objects.filter(
        Q(experience_level='entry') | Q(job_type='internship')
    ).select_related('company').distinct()[:6]

    return render(request, 'careers/highschool.html', {
        'title': 'High School Careers in South Africa - future careers, university options and early learning paths',
        'entry_level_jobs': recommended_jobs,
    })

def past_papers(request):
    subjects = Subject.objects.all()

    selected_grade = request.GET.get('grade')
    selected_subject = request.GET.get('subject')

    filters = {}
    if selected_grade:
        filters['grade'] = selected_grade
    if selected_subject:
        filters['subject__name__icontains'] = selected_subject

    if filters:
        filtered_papers = PastPaper.objects.filter(**filters)
        papers_by_grade = {'Filtered Results': filtered_papers}  # one key for filtered results
        show_top_downloaded = False
    else:
        papers_by_grade = {
            'Grade 12': PastPaper.objects.filter(grade='Grade 12'),
            'Grade 11': PastPaper.objects.filter(grade='Grade 11'),
            'Grade 10': PastPaper.objects.filter(grade='Grade 10'),
        }
        show_top_downloaded = True

    top_downloaded_papers = PastPaper.objects.order_by('-download_count')[:3]

    return render(request, 'careers/past-papers.html', {
        'title': 'Past Papers in South Africa',
        'subjects': subjects,
        'papers_by_grade': papers_by_grade,
        'top_downloaded_papers': top_downloaded_papers,
        'selected_grade': selected_grade,
        'selected_subject': selected_subject,
        'show_top_downloaded': show_top_downloaded,
    })




# def past_papers(request):
#     subjects = Subject.objects.all()
#     all_papers = PastPaper.objects.select_related('subject')

#     papers_by_grade = {
#         'Grade 12': all_papers.filter(grade='Grade 12'),
#         'Grade 11': all_papers.filter(grade='Grade 11'),
#         'Grade 10': all_papers.filter(grade='Grade 10'),
#     }

#     top_downloaded_papers = all_papers.order_by('-download_count')[:3]

#     return render(request, 'careers/past-papers.html', {
#         'title': 'Past Papers in South Africa',
#         'subjects': subjects,
#         'papers_by_grade': papers_by_grade,
#         'top_downloaded_papers': top_downloaded_papers,
#     })






def download_paper(request, paper_id, file_type='file'):
    paper = get_object_or_404(PastPaper, id=paper_id)

    file_to_download = getattr(paper, file_type, None)
    if not file_to_download:
        raise Http404("File not found")

    try:
        paper.download_count = F('download_count') + 1
        paper.save(update_fields=['download_count'])
        paper.refresh_from_db(fields=['download_count'])
        return FileResponse(file_to_download.open(), as_attachment=True, filename=os.path.basename(file_to_download.name))
    except Exception:
        raise Http404("Error serving the file")
    


def graduates_opportunities(request):

    latest_articles = Article.objects.filter(status='published').order_by('-published_at')[:6]

    articles = Article.objects.filter(
        status=Article.STATUS_PUBLISHED,
        tags__name__icontains='student'
    ).order_by('-published_at').distinct()[:5]

    return render(request, 'careers/graduates.html', {
        'title': 'Graduate Opportunities in South Africa',
        'latest_articles': latest_articles,
        'recommended_articles': articles,
    })



def graduates_internships(request):
    return render(request, 'careers/graduate-internships.html', {
        'title': 'Graduate Internships in South Africa',
    })


def postgraduate_bursaries(request):
    bursaries = Bursary.objects.all()
    return render(request, 'careers/postgraduate-bursaries.html', {
        'title': 'Postgraduate Bursaries in South Africa',
        'bursaries': bursaries
    })



def get_certifications(request):
    certifications = Certification.objects.all()

    query = request.GET.get('q')
    price_filter = request.GET.get('price')
    sort = request.GET.get('sort')

    # Search
    if query:
        certifications = certifications.filter(
            Q(title__icontains=query) | Q(description__icontains=query)
        )

    # Filter by price type (Free / Paid)
    if price_filter in ['Free', 'Paid']:
        certifications = certifications.filter(price_type__iexact=price_filter)

    # Sort
    if sort == 'popular':
        certifications = certifications.order_by('-students_enrolled')
    elif sort == 'latest':
        certifications = certifications.order_by('-id')

    return render(request, 'careers/certificates.html', {
        'title': 'Get Certifications in South Africa',
        'certifications': certifications,
        'total': certifications.count(),
        'query': query or '',
        'active_price': price_filter or '',
        'active_sort': sort or '',
    })




# Articles Views 

def article_list(request):
    articles = Article.objects.filter(status='published').order_by('-published_at')
    return render(request, 'articles/articles.html', {
        'title': 'South African Articles',
        'articles': articles,
    })



def article_detail(request, pk, slug):
    article = get_object_or_404(Article, pk=pk, slug=slug)
    article.view_count += 1
    article.save()

    title = f"{article.title} | Mzansi Plug Articles"
    return render(request, 'articles/article-detail.html', {'article': article , 'title': title })

def tagged_articles(request, tag_slug):
    tag = get_object_or_404(Tag, slug=tag_slug)

    articles = Article.objects.filter(tags__slug__in=[tag_slug], status=Article.STATUS_PUBLISHED) 

    return render(request, 'articles/tagged-articles.html', {'tag': tag , 'articles': articles , 'title': tag})


def category_articles(request , pk , category_slug):
    print('PK', pk)
    print(category_slug)
    category = get_object_or_404(ArticleCategory, pk=pk , slug=category_slug)
    print("CATEGORY", category)

    articles = Article.objects.filter(slug=[category_slug], status=Article.STATUS_PUBLISHED) 

    return render(request, 'articles/category-articles.html', {'category': category , 'articles': articles , 'title': category})


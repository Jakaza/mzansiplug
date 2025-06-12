from django.shortcuts import render
from django.db.models import Prefetch
from django.db.models import Q
from .models import Job , Category
from django.shortcuts import get_object_or_404
from django.contrib.sites.shortcuts import get_current_site
from django.contrib.admin.views.decorators import staff_member_required


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

    return render(request, 'index.html', {
        'categories': categories,
        'jobs': jobs,
        'selected_category': selected_category,
        'title': 'Welcome to MzansiPlug - South African Jobs and Salaries Platform',
    })



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


# Salaries Views

def salary_list(request):
    return render(request, 'salaries/salaries.html', {
        'title': 'Latest Salaries in South Africa – Compare Wages by Industry & Role',
    })



# Careers Views 

def career_list(request):
    return render(request, 'careers/careers.html', {
        'title': 'South African Careers',
    })


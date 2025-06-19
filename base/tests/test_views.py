from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from base.models import Category, Job, Article, CompanyProfile , SubCategory , SalaryReport
from django.utils.text import slugify
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image
import tempfile
from django.utils import timezone

from django.test import TestCase, RequestFactory
from django.urls import reverse
from django.contrib.sites.models import Site


User = get_user_model()


def get_dummy_image_file(name='test.jpg'):
    file = BytesIO()
    image = Image.new('RGB', (100, 100))
    image.save(file, 'JPEG')
    file.seek(0)
    return SimpleUploadedFile(name, file.read(), content_type='image/jpeg')

class IndexViewTests(TestCase):

    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')

        self.company = CompanyProfile.objects.create(user=self.user, company_name='Test Company')

        self.category1 = Category.objects.create(name='IT')
        self.category2 = Category.objects.create(name='Health')

        self.job1 = Job.objects.create(
            title='Developer',
            company=self.company,
            location='Pretoria',
            description='Develop stuff',
        )
        self.job1.categories.add(self.category1)

        self.article = Article.objects.create(
            title='Top Article',
            author=self.user,
            content='Top article content',
            status='published',
            view_count=100,
            cover_image=get_dummy_image_file(),
        )

    def test_index_view_status_code(self):
        response = self.client.get(reverse('index'))  # Make sure your urls.py uses name='home'
        self.assertEqual(response.status_code, 200)

    def test_index_view_shows_only_categories_with_jobs(self):
        response = self.client.get(reverse('index'))
        categories = response.context['categories']
        self.assertIn(self.category1, categories)
        self.assertNotIn(self.category2, categories)  # No job assigned to category2

    def test_index_view_filters_jobs_by_category(self):
        response = self.client.get(reverse('index') + f'?category={self.category1.slug}')
        jobs = response.context['jobs']
        self.assertIn(self.job1, jobs)

    def test_index_view_context_includes_latest_job_and_top_article(self):
        response = self.client.get(reverse('index'))
        self.assertEqual(response.context['latest_job'], self.job1)
        self.assertEqual(response.context['top_article'], self.article)




class JobListViewTests(TestCase):
    def setUp(self):
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.company = CompanyProfile.objects.create(user=self.user, company_name='TestCorp')
        self.category = Category.objects.create(name='Engineering')
        self.subcategory = SubCategory.objects.create(name='Software', category=self.category)

        self.job = Job.objects.create(
            title='Backend Developer',
            company=self.company,
            location='Pretoria',
            description='Work on APIs',
            job_type='full_time',
            experience_level='entry'
        )
        self.job.categories.add(self.category)
        self.job.subcategories.add(self.subcategory)

        self.article = Article.objects.create(
            title='Top 5 Tech Skills',
            content='Content here',
            author=self.user,
            status='published',
            published_at=timezone.now(),
        )

    def test_job_list_status_code(self):
        response = self.client.get(reverse('south-african-jobs'))  # Adjust name if different
        self.assertEqual(response.status_code, 200)

    def test_job_list_returns_jobs(self):
        response = self.client.get(reverse('south-african-jobs'))
        self.assertContains(response, 'Backend Developer')

    def test_filter_by_role(self):
        response = self.client.get(reverse('south-african-jobs'), {'role': 'Back'})
        self.assertContains(response, 'Backend Developer')

    def test_filter_by_location(self):
        response = self.client.get(reverse('south-african-jobs'), {'location': 'Pretoria'})
        self.assertContains(response, 'Pretoria')

    def test_filter_by_job_type(self):
        response = self.client.get(reverse('south-african-jobs'), {'job_type': 'full_time'})
        self.assertContains(response, 'Backend Developer')

    def test_filter_by_experience_level(self):
        response = self.client.get(reverse('south-african-jobs'), {'experience_level': 'entry'})
        self.assertContains(response, 'Backend Developer')

    def test_sort_by_date(self):
        response = self.client.get(reverse('south-african-jobs'), {'sort': 'date'})
        self.assertEqual(response.status_code, 200)

    def test_sort_by_salary_high(self):
        self.job.salary = 10000
        self.job.save()
        response = self.client.get(reverse('south-african-jobs'), {'sort': 'salary_high'})
        self.assertEqual(response.status_code, 200)

    def test_context_contains_filters(self):
        response = self.client.get(reverse('south-african-jobs'), {'role': 'Backend'})
        self.assertIn('filters', response.context)
        self.assertEqual(response.context['filters']['role'], 'Backend')

    def test_context_includes_articles_and_latest_job(self):
        response = self.client.get(reverse('south-african-jobs'))
        self.assertEqual(response.context['latest_job'], self.job)
        self.assertEqual(response.context['top_article'], self.article)
        self.assertEqual(len(response.context['related_articles']), 1)


class JobDetailViewTest(TestCase):
    def setUp(self):
        # Create a CompanyProfile
        self.user = User.objects.create_user(username='testuser', password='testpass')
        self.company = CompanyProfile.objects.create(user=self.user, company_name="Test Company")

        # Create Categories
        self.cat1 = Category.objects.create(name="Engineering")
        self.cat2 = Category.objects.create(name="IT")

        # Create Job
        self.job = Job.objects.create(
            title="Senior Developer",
            company=self.company,
            location="Cape Town",
            description="Job description here",
            internal_or_external='internal',
        )
        self.job.categories.set([self.cat1, self.cat2])
        self.job.save()

        # Create another job to be a related job
        self.related_job = Job.objects.create(
            title="Junior Developer",
            company=self.company,
            location="Cape Town",
            description="Another job",
            internal_or_external='internal',
        )
        self.related_job.categories.set([self.cat1])
        self.related_job.save()

        # Create SalaryReport related to the same category
        self.salary_report = SalaryReport.objects.create(
            title="Developer Salary",
            low_salary=30000,
            average_salary=50000,
            high_salary=70000,
            salary_type='yearly',
            overview="Salary overview"
        )
        self.salary_report.categories.set([self.cat1])
        self.salary_report.save()

        self.factory = RequestFactory()
        self.site = Site.objects.get_current()


    def test_job_detail_view(self):
        url = reverse('job-detail', kwargs={'pk': self.job.pk, 'slug': self.job.slug})
        
        # Use self.client to get the page (simulate a real HTTP request)
        response = self.client.get(url)
        
        self.assertEqual(response.status_code, 200)
        
        # Now you can check templates and context
        self.assertIn('jobs/job-detail.html', [t.name for t in response.templates])
        
        self.job.refresh_from_db()
        self.assertEqual(self.job.views, 1)
        
        self.assertEqual(response.context['job'], self.job)
        
        related_jobs = response.context['related_jobs']
        self.assertIn(self.related_job, related_jobs)
        self.assertNotIn(self.job, related_jobs)
        
        related_salaries = response.context['related_salaries']
        self.assertIn(self.salary_report, related_salaries)
        
        expected_title = f"{self.job.title} at {self.job.company.company_name} – {self.job.location} | Mzansi Plug Jobs"
        self.assertEqual(response.context['title'], expected_title)
        
        self.assertTrue(response.context['job_url'].startswith('http'))

        

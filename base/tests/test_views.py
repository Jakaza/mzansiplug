from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from base.models import Category, Job, Article, CompanyProfile , SubCategory
from django.utils.text import slugify
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image
import tempfile
from django.utils import timezone


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

from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model
from base.models import Category, Job, Article, CompanyProfile
from django.utils.text import slugify
from django.core.files.uploadedfile import SimpleUploadedFile
from io import BytesIO
from PIL import Image

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

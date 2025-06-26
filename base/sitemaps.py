from django.contrib.sitemaps import Sitemap
from django.shortcuts import reverse
from base.models import Job, SalaryReport as Salary, Article, Certification

class StaticViewSitemap(Sitemap):
    priority = 0.8
    changefreq = 'weekly'

    def items(self):
        return ['index', 'south-african-jobs', 'south-african-salaries', 'south-african-careers',
                'get-certificates', 'about-us', 'contact', 'privacy-policy', 'terms-and-conditions', 'disclaimer']

    def location(self, item):
        return reverse(item)

class JobSitemap(Sitemap):
    changefreq = "daily"
    priority = 0.9

    def items(self):
        return Job.objects.all()

    def location(self, obj):
        return reverse('job-detail', args=[obj.pk, obj.slug])

class SalarySitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.7

    def items(self):
        return Salary.objects.all()

    def location(self, obj):
        return reverse('salary-detail', args=[obj.pk, obj.slug])

class ArticleSitemap(Sitemap):
    changefreq = "weekly"
    priority = 0.8

    def items(self):
        return Article.objects.all()

    def location(self, obj):
        return reverse('article-detail', args=[obj.pk, obj.slug])

class CertificateSitemap(Sitemap):
    changefreq = "monthly"
    priority = 0.6

    def items(self):
        return Certification.objects.all()

    def location(self, obj):
        return reverse('get-certificates')

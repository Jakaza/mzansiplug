from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

from django.contrib.sitemaps.views import sitemap
from base.sitemaps import StaticViewSitemap, JobSitemap, SalarySitemap, ArticleSitemap, CertificateSitemap

# ✅ Define sitemap dictionary
sitemaps_dict = {
    'static': StaticViewSitemap,
    'jobs': JobSitemap,
    'salaries': SalarySitemap,
    'articles': ArticleSitemap,
    'certificates': CertificateSitemap,
}

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('base.urls')),
    path('candidate/', include('candidate.urls')),

    # ✅ Sitemap route
    path('sitemap.xml', sitemap, {'sitemaps': sitemaps_dict}, name='django.contrib.sitemaps.views.sitemap'),
]

# Media file handling in DEBUG
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

# Custom 404
handler404 = 'base.views.custom_404'

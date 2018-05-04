from django.conf import settings
from django.conf.urls.static import static
from django.conf.urls import include, url
from django.conf.urls.i18n import i18n_patterns
from django.contrib import admin
from django.contrib.sitemaps.views import sitemap
from django.core.urlresolvers import reverse_lazy
from django.views.generic import TemplateView, RedirectView

from . import views


urlpatterns = [
    url(r'^about/$', views.about, name='about'),
    url(r'^grappelli/', include('grappelli.urls')),
    url(r'^admin/login/', RedirectView.as_view(url=reverse_lazy('login'), permanent=False)),
    url(r'^admin/', include(admin.site.urls)),
    url(r'^sitemap\.xml$', sitemap, {'sitemaps': views.static_sitemap},
        name='django.contrib.sitemaps.views.sitemap'),
    url(r'^robots\.txt', TemplateView.as_view(template_name='robots.txt'))
]

# The following urls are created with the locale as prefix, eg.
# en/questionnaire
urlpatterns += i18n_patterns(
    url(r'^$', RedirectView.as_view(
        url=reverse_lazy('wocat:home'),
        permanent=False
    ), name='home'),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^api/', include('api.urls')),
    url(r'^configuration', include('configuration.urls', namespace='configuration')),
    url(r'^notifications/', include('notifications.urls')),
    url(r'^qcat/facts_teaser', views.FactsTeaserView.as_view(), name='facts_teaser'),
    url(r'^questionnaire/', include('questionnaire.urls')),
    url(r'^search/', include('search.urls', namespace='search')),
    url(r'^summary/', include('summary.urls')),
    url(r'^unccd/', include('unccd.urls', namespace='unccd')),
    url(r'^wocat/', include('wocat.urls', namespace='wocat')),
    url(r'^wocat/approaches/', include('approaches.urls',
        namespace='approaches')),
    url(r'^wocat/cca/', include('cca.urls', namespace='cca')),
    url(r'^wocat/technologies/', include('technologies.urls',
        namespace='technologies')),
    url(r'^wocat/watershed/', include(
        'watershed.urls', namespace='watershed')),
)

if settings.DEBUG:
    urlpatterns += i18n_patterns(
        url(r'^sample/', include('sample.urls', namespace='sample')),
        url(r'^samplemulti/', include('samplemulti.urls',
            namespace='samplemulti')),
        url(r'^samplemodule/',
            include('samplemodule.urls', namespace='samplemodule')),
        url(r'^404/', TemplateView.as_view(template_name='404.html')),
        url(r'^500/', TemplateView.as_view(template_name='500.html')),
        url(r'^503/', TemplateView.as_view(template_name='503.html')),
    ) + static(
        settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)

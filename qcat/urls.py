from django.conf.urls import patterns, include, url
from django.conf.urls.i18n import i18n_patterns
# from django.contrib import admin

urlpatterns = patterns(
    '',

    url(r'^$', 'qcat.views.home', name='home'),

    # View to change language
    url(r'^i18n/', include('django.conf.urls.i18n')),

    # url(r'^admin/', include(admin.site.urls)),
)

# The following urls are created with the locale as prefix, eg.
# en/questionnaire
urlpatterns += i18n_patterns(
    '',
    url(r'^questionnaire/', include('questionnaire.urls')),
)

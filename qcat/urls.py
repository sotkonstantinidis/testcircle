from django.conf.urls import patterns, include, url
from django.conf.urls.i18n import i18n_patterns

urlpatterns = patterns(
    '',

    url(r'^$', 'qcat.views.home', name='home'),
    url(r'^about/$', 'qcat.views.about', name='about'),

    # View to change language
    url(r'^i18n/', include('django.conf.urls.i18n')),
)

# The following urls are created with the locale as prefix, eg.
# en/questionnaire
urlpatterns += i18n_patterns(
    '',
    url(r'^questionnaire/', include('questionnaire.urls')),
    url(r'^accounts/', include('accounts.urls')),
    url(r'^unccd/', include('unccd.urls')),
)

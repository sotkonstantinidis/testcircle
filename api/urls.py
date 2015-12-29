from django.conf.urls import patterns, url, include
from rest_framework.urlpatterns import format_suffix_patterns

from .views import APIRoot


urlpatterns = patterns(
    '',
    url(r'^$', APIRoot.as_view(), name='api-root'),
)

urlpatterns = format_suffix_patterns(urlpatterns)
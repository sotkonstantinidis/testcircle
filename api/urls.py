from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns

from .views import APIRoot, QuestionnairesAPIListView


urlpatterns = patterns(
    '',
    url(r'^$', APIRoot.as_view(), name='api-root'),
    url(r'^technologies/$', QuestionnairesAPIListView.as_view(), name='questionnaires-api-list'),
)

urlpatterns = format_suffix_patterns(urlpatterns)
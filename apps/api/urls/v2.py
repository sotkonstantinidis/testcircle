from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns

from questionnaire.api import views


urlpatterns = patterns(
    '',
    url(r'^questionnaires/$',
        views.QuestionnaireListView.as_view(),
        name='questionnaires-api-list'
        ),
    url(r'^questionnaires/(?P<identifier>[^/]+)/$',
        views.ConfiguredQuestionnaireDetailView.as_view(),
        name='questionnaires-api-detail',
        ),
)

urlpatterns = format_suffix_patterns(urlpatterns)

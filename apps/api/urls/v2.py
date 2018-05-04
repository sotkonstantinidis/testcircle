from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from questionnaire.api import views


urlpatterns = [
    url(r'^questionnaires/$',
        views.QuestionnaireListView.as_view(),
        name='questionnaires-api-list'
        ),
    url(r'^questionnaires/(?P<identifier>[^/]+)/$',
        views.ConfiguredQuestionnaireDetailView.as_view(),
        name='questionnaires-api-detail',
        ),
]

urlpatterns = format_suffix_patterns(urlpatterns)

from django.conf.urls import patterns, url
from rest_framework.urlpatterns import format_suffix_patterns

from questionnaire.api.views import QuestionnaireViewSet

from .views import APIRoot


questionnaire_list = QuestionnaireViewSet.as_view({
    'get': 'list'
})
questionnaire_detail = QuestionnaireViewSet.as_view({
    'get': 'retrieve'
})


urlpatterns = patterns(
    '',
    url(r'^$', APIRoot.as_view(), name='api-root'),
    url(r'^questionnaire/$',
        questionnaire_list,
        name='questionnaires-api-list'
        ),
    url(r'^questionnaire/(?P<pk>[0-9]+)/$',
        questionnaire_detail,
        name='questionnaires-api-detail'
        ),
)

urlpatterns = format_suffix_patterns(urlpatterns)

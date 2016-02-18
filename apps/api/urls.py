from django.conf import settings
from django.conf.urls import patterns, url, include
from django.views.decorators.cache import cache_page
from rest_framework.authtoken.views import obtain_auth_token
from rest_framework.urlpatterns import format_suffix_patterns

from questionnaire.api.views import QuestionnaireViewSet

from .views import APIRoot


questionnaire_list = QuestionnaireViewSet.as_view({
    'get': 'list'
})
questionnaire_detail = QuestionnaireViewSet.as_view({
    'get': 'retrieve'
})
api_root_patterns = [
    url(r'^$', APIRoot.as_view(), name='api-root'),
]

urlpatterns = patterns(
    '',
    url(r'^questionnaires/$',
        cache_page(settings.CACHE_TIMEOUT)(questionnaire_list),
        name='questionnaires-api-list'
        ),
    url(r'^questionnaires/(?P<pk>[0-9]+)/$',
        cache_page(settings.CACHE_TIMEOUT)(questionnaire_detail),
        name='questionnaires-api-detail'
        ),
    url(r'^auth-token/$', obtain_auth_token, name='obtain-api-token'),
    url(r'^docs/', include('rest_framework_swagger.urls')),
)

# Workaround: the api root must not be in the API docs. Only namespaces can
# be excluded - so a namespace is created for this single view.
urlpatterns = urlpatterns + patterns(
    '',
    url(r'^$', include((api_root_patterns, 'api', 'api-root'))),
)

urlpatterns = format_suffix_patterns(urlpatterns)

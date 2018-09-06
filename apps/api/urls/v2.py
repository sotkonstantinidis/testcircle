from django.conf.urls import url
from rest_framework.urlpatterns import format_suffix_patterns

from questionnaire.api import views as questionnaire_views
from configuration.api import views as configuration_views


urlpatterns = [
    url(r'^questionnaires/$',
        questionnaire_views.QuestionnaireListView.as_view(),
        name='questionnaires-api-list'
    ),
    url(r'^questionnaires/(?P<identifier>[^/]+)/$',
        questionnaire_views.ConfiguredQuestionnaireDetailView.as_view(),
        name='questionnaires-api-detail',
    ),
    url(r'^configuration/(?P<code>[^/]+)/(?P<edition>[^/]+)/$',
        configuration_views.ConfigurationStructureView.as_view(),
        name='api-configuration-structure',
    ),
]

urlpatterns = format_suffix_patterns(urlpatterns)

from django.conf.urls import url, patterns

from questionnaire.views import GenericQuestionnaireView, GenericQuestionnaireStepView

urlpatterns = patterns(
    '',
    url(r'^view/(?P<identifier>[^/]+)/$',
        'samplemodule.views.questionnaire_details',
        name='questionnaire_details'),
    url(r'^edit/new/$', GenericQuestionnaireView.as_view(url_namespace=__package__),
        name='questionnaire_new'),
    url(r'^edit/(?P<identifier>[^/]+)/$',
        GenericQuestionnaireView.as_view(url_namespace=__package__),
        name='questionnaire_edit'),
    url(r'^edit/(?P<identifier>[^/]+)/(?P<step>\w+)/$',
        GenericQuestionnaireStepView.as_view(url_namespace=__package__),
        name='questionnaire_new_step'),
)

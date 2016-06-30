from django.conf.urls import url, patterns

from questionnaire.views import GenericQuestionnaireView, GenericQuestionnaireStepView

urlpatterns = patterns(
    '',
    url(r'^$', 'sample.views.home', name='home'),
    url(r'^view/(?P<identifier>[^/]+)/$', 'sample.views.questionnaire_details',
        name='questionnaire_details'),
    url(r'^view/(?P<identifier>[^/]+)/map/$',
        'sample.views.questionnaire_view_map',
        name='questionnaire_view_map'),
    url(r'^view/(?P<identifier>[^/]+)/(?P<step>\w+)/$',
        'sample.views.questionnaire_view_step',
        name='questionnaire_view_step'),
    url(r'^edit/new/$', GenericQuestionnaireView.as_view(url_namespace=__package__),
        name='questionnaire_new'),
    url(r'^edit/(?P<identifier>[^/]+)/$', GenericQuestionnaireView.as_view(url_namespace=__package__),
        name='questionnaire_edit'),
    url(r'^edit/(?P<identifier>[^/]+)/(?P<step>\w+)/$',
        GenericQuestionnaireStepView.as_view(url_namespace=__package__), name='questionnaire_new_step'),
    url(r'^search/links/$', 'sample.views.questionnaire_link_search',
        name='questionnaire_link_search'),
    url(r'^list/$', 'sample.views.questionnaire_list',
        name='questionnaire_list'),
    url(r'^list_partial/$', 'sample.views.questionnaire_list_partial',
        name='questionnaire_list_partial'),
)

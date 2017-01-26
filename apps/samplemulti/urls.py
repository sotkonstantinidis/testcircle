from django.conf.urls import url, patterns

from questionnaire.views import QuestionnaireEditView, GenericQuestionnaireStepView

urlpatterns = patterns(
    '',
    url(r'^$', 'samplemulti.views.home', name='home'),
    url(r'^view/(?P<identifier>[^/]+)/$',
        'samplemulti.views.questionnaire_details',
        name='questionnaire_details'),
    url(r'^view/(?P<identifier>[^/]+)/(?P<step>\w+)/$',
        'samplemulti.views.questionnaire_view_step',
        name='questionnaire_view_step'),
    url(r'^edit/new/$', QuestionnaireEditView.as_view(url_namespace=__package__),
        name='questionnaire_new'),
    url(r'^edit/(?P<identifier>[^/]+)/$', QuestionnaireEditView.as_view(url_namespace=__package__),
        name='questionnaire_edit'),
    url(r'^edit/(?P<identifier>[^/]+)/(?P<step>\w+)/$',
        GenericQuestionnaireStepView.as_view(url_namespace=__package__), name='questionnaire_new_step'),
    url(r'^search/links/$', 'samplemulti.views.questionnaire_link_search',
        name='questionnaire_link_search'),
    url(r'^list/$', 'samplemulti.views.questionnaire_list',
        name='questionnaire_list'),
    url(r'^list_partial/$', 'samplemulti.views.questionnaire_list_partial',
        name='questionnaire_list_partial'),
)

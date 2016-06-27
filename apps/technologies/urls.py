from django.conf.urls import url, patterns

from questionnaire.views import GenericQuestionnaireView, GenericQuestionnaireStepView

urlpatterns = patterns(
    '',
    # The 'home' route points to the list
    url(r'^$', 'technologies.views.questionnaire_list', name='home'),
    url(r'^view/(?P<identifier>[^/]+)/$',
        'technologies.views.questionnaire_details',
        name='questionnaire_details'),
    url(r'^view/(?P<identifier>[^/]+)/(?P<step>\w+)/$',
        'technologies.views.questionnaire_view_step',
        name='questionnaire_view_step'),
    url(r'^edit/new/$', GenericQuestionnaireView.as_view(url_namespace=__package__),
        name='questionnaire_new'),
    url(r'^edit/(?P<identifier>[^/]+)/$', GenericQuestionnaireView.as_view(url_namespace=__package__),
        name='questionnaire_edit'),
    url(r'^edit/(?P<identifier>[^/]+)/(?P<step>\w+)/$',
        GenericQuestionnaireStepView.as_view(url_namespace=__package__),
        name='questionnaire_new_step'),
    url(r'^search/links/$', 'technologies.views.questionnaire_link_search',
        name='questionnaire_link_search'),
    url(r'^list/$', 'technologies.views.questionnaire_list',
        name='questionnaire_list'),
    url(r'^list_partial/$', 'technologies.views.questionnaire_list_partial',
        name='questionnaire_list_partial'),
)

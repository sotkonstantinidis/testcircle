from django.conf.urls import url, patterns

from questionnaire.views import GenericQuestionnaireView

urlpatterns = patterns(
    '',
    # The 'home' route points to the list
    url(r'^$', 'approaches.views.questionnaire_list', name='home'),
    url(r'^view/(?P<identifier>[^/]+)/$',
        'approaches.views.questionnaire_details',
        name='questionnaire_details'),
    url(r'^view/(?P<identifier>[^/]+)/(?P<step>\w+)/$',
        'approaches.views.questionnaire_view_step',
        name='questionnaire_view_step'),
    url(r'^edit/new/$', GenericQuestionnaireView.as_view(url_namespace='approaches'),
        name='questionnaire_new'),
    url(r'^edit/(?P<identifier>[^/]+)/$', GenericQuestionnaireView.as_view(url_namespace='approaches'),
        name='questionnaire_edit'),
    url(r'^edit/(?P<identifier>[^/]+)/(?P<step>\w+)/$',
        'approaches.views.questionnaire_new_step',
        name='questionnaire_new_step'),
    url(r'^search/links/$', 'approaches.views.questionnaire_link_search',
        name='questionnaire_link_search'),
    url(r'^list/$', 'approaches.views.questionnaire_list',
        name='questionnaire_list'),
    url(r'^list_partial/$', 'approaches.views.questionnaire_list_partial',
        name='questionnaire_list_partial'),
)

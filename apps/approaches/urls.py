from django.conf.urls import url, patterns

urlpatterns = patterns(
    '',
    # The 'home' route points to the list
    url(r'^$', 'approaches.views.questionnaire_list', name='home'),
    url(r'^view/(?P<identifier>\w+)/$',
        'approaches.views.questionnaire_details',
        name='questionnaire_details'),
    url(r'^view/(?P<identifier>\w+)/(?P<step>\w+)/$',
        'approaches.views.questionnaire_view_step',
        name='questionnaire_view_step'),
    url(r'^edit/new/$', 'approaches.views.questionnaire_new',
        name='questionnaire_new'),
    url(r'^edit/(?P<identifier>\w+)/$', 'approaches.views.questionnaire_new',
        name='questionnaire_edit'),
    url(r'^edit/(?P<identifier>\w+)/(?P<step>\w+)/$',
        'approaches.views.questionnaire_new_step',
        name='questionnaire_new_step'),
    url(r'^search/links/$', 'approaches.views.questionnaire_link_search',
        name='questionnaire_link_search'),
    url(r'^list/$', 'approaches.views.questionnaire_list',
        name='questionnaire_list'),
    url(r'^list_partial/$', 'approaches.views.questionnaire_list_partial',
        name='questionnaire_list_partial'),
)

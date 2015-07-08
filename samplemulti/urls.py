from django.conf.urls import url, patterns

urlpatterns = patterns(
    '',
    url(r'^$', 'samplemulti.views.home', name='home'),
    url(r'^view/(\d+)/$', 'samplemulti.views.questionnaire_details',
        name='questionnaire_details'),
    url(r'^edit/$', 'samplemulti.views.questionnaire_new',
        name='questionnaire_new'),
    url(r'^edit/(\d+)/$', 'samplemulti.views.questionnaire_new',
        name='questionnaire_edit'),
    url(r'^edit/links/$', 'samplemulti.views.questionnaire_link_form',
        name='questionnaire_link_form'),
    url(r'^search/links/$', 'samplemulti.views.questionnaire_link_search',
        name='questionnaire_link_search'),
    url(r'^edit/(?P<step>\w+)/$', 'samplemulti.views.questionnaire_new_step',
        name='questionnaire_new_step'),
    url(r'^list/$', 'samplemulti.views.questionnaire_list',
        name='questionnaire_list'),
    url(r'^list_partial/$', 'samplemulti.views.questionnaire_list_partial',
        name='questionnaire_list_partial'),
)

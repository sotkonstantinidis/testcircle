from django.conf.urls import url, patterns

urlpatterns = patterns(
    '',
    # The 'home' route points to the list
    url(r'^$', 'approaches.views.questionnaire_list', name='home'),
    url(r'^view/(\d+)/$', 'approaches.views.questionnaire_details',
        name='questionnaire_details'),
    url(r'^edit/$', 'approaches.views.questionnaire_new',
        name='questionnaire_new'),
    url(r'^edit/(\d+)/$', 'approaches.views.questionnaire_new',
        name='questionnaire_edit'),
    url(r'^edit/links/$', 'approaches.views.questionnaire_link_form',
        name='questionnaire_link_form'),
    url(r'^search/links/$', 'approaches.views.questionnaire_link_search',
        name='questionnaire_link_search'),
    url(r'^edit/(?P<step>\w+)/$', 'approaches.views.questionnaire_new_step',
        name='questionnaire_new_step'),
    url(r'^list/$', 'approaches.views.questionnaire_list',
        name='questionnaire_list'),
    url(r'^list_partial/$', 'approaches.views.questionnaire_list_partial',
        name='questionnaire_list_partial'),
)

from django.conf.urls import url, patterns

urlpatterns = patterns(
    '',
    # The 'home' route points to the list
    url(r'^$', 'technologies.views.questionnaire_list', name='home'),
    url(r'^view/(\d+)/$', 'technologies.views.questionnaire_details',
        name='questionnaire_details'),
    url(r'^edit/$', 'technologies.views.questionnaire_new',
        name='questionnaire_new'),
    url(r'^edit/(\d+)/$', 'technologies.views.questionnaire_new',
        name='questionnaire_edit'),
    url(r'^edit/links/$', 'technologies.views.questionnaire_link_form',
        name='questionnaire_link_form'),
    url(r'^search/links/$', 'technologies.views.questionnaire_link_search',
        name='questionnaire_link_search'),
    url(r'^edit/(?P<step>\w+)/$', 'technologies.views.questionnaire_new_step',
        name='questionnaire_new_step'),
    url(r'^list/$', 'technologies.views.questionnaire_list',
        name='questionnaire_list'),
    url(r'^list_partial/$', 'technologies.views.questionnaire_list_partial',
        name='questionnaire_list_partial'),
)

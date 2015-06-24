from django.conf.urls import url, patterns

urlpatterns = patterns(
    '',
    url(r'^$', 'unccd.views.home', name='home'),
    url(r'^view/(\d+)/$', 'unccd.views.questionnaire_details',
        name='questionnaire_details'),
    url(r'^edit/$', 'unccd.views.questionnaire_new',
        name='questionnaire_new'),
    url(r'^edit/(\d+)/$', 'unccd.views.questionnaire_new',
        name='questionnaire_edit'),
    url(r'^edit/(?P<step>\w+)/$', 'unccd.views.questionnaire_new_step',
        name='questionnaire_new_step'),
    url(r'^list/$', 'unccd.views.questionnaire_list',
        name='questionnaire_list'),
    url(r'^list_partial/$', 'unccd.views.questionnaire_list_partial',
        name='questionnaire_list_partial'),
    url(r'^search/$', 'unccd.views.search', name='search'),
)

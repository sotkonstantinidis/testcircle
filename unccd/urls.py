from django.conf.urls import url, patterns

urlpatterns = patterns(
    '',
    url(r'^$', 'unccd.views.home', name='unccd_home'),
    url(r'^view/(\d+)/$', 'unccd.views.questionnaire_details',
        name='unccd_questionnaire_details'),
    url(r'^edit/$', 'unccd.views.questionnaire_new',
        name='unccd_questionnaire_new'),
    url(r'^edit/(\d+)/$', 'unccd.views.questionnaire_new',
        name='unccd_questionnaire_edit'),
    url(r'^edit/(?P<step>\w+)/$', 'unccd.views.questionnaire_new_step',
        name='unccd_questionnaire_new_step'),
    url(r'^list/$', 'unccd.views.questionnaire_list',
        name='unccd_questionnaire_list'),
)

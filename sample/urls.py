from django.conf.urls import url, patterns

urlpatterns = patterns(
    '',
    url(r'^$', 'sample.views.home', name='sample_home'),
    url(r'^view/(\d+)/$', 'sample.views.questionnaire_details',
        name='sample_questionnaire_details'),
    url(r'^edit/$', 'sample.views.questionnaire_new',
        name='sample_questionnaire_new'),
    url(r'^edit/(\d+)/$', 'sample.views.questionnaire_new',
        name='sample_questionnaire_edit'),
    url(r'^edit/(?P<step>\w+)/$', 'sample.views.questionnaire_new_step',
        name='sample_questionnaire_new_step'),
    url(r'^list/$', 'sample.views.questionnaire_list',
        name='sample_questionnaire_list'),
)

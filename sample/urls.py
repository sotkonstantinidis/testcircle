from django.conf.urls import url, patterns

urlpatterns = patterns(
    '',
    url(r'^$', 'sample.views.home', name='home'),
    url(r'^view/(\d+)/$', 'sample.views.questionnaire_details',
        name='questionnaire_details'),
    url(r'^edit/$', 'sample.views.questionnaire_new',
        name='questionnaire_new'),
    url(r'^edit/(\d+)/$', 'sample.views.questionnaire_new',
        name='questionnaire_edit'),
    url(r'^edit/(?P<step>\w+)/$', 'sample.views.questionnaire_new_step',
        name='questionnaire_new_step'),
    url(r'^list/$', 'sample.views.questionnaire_list',
        name='questionnaire_list'),
)

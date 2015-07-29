from django.conf.urls import url, patterns

urlpatterns = patterns(
    '',
    url(r'^$', 'wocat.views.home', name='home'),
    url(r'^view/(?P<identifier>\w+)/$', 'wocat.views.questionnaire_details',
        name='questionnaire_details'),
    url(r'^list/$', 'wocat.views.questionnaire_list',
        name='questionnaire_list'),
    url(r'^list_partial/$', 'wocat.views.questionnaire_list_partial',
        name='questionnaire_list_partial'),
)

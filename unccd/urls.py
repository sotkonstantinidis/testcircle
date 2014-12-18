from django.conf.urls import url, patterns

urlpatterns = patterns(
    '',
    url(r'^$', 'unccd.views.home', name='unccd_home'),
    url(r'^new/$', 'unccd.views.questionnaire_new',
        name='unccd_questionnaire_new'),
    url(r'^new/(?P<step>\w+)/$', 'unccd.views.questionnaire_new_step',
        name='unccd_questionnaire_new_step'),
)

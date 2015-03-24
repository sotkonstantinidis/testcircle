from django.conf.urls import url, patterns

urlpatterns = patterns(
    '',
    url(r'^$', 'wocat.views.home', name='home'),
    url(r'^edit/$', 'wocat.views.questionnaire_new',
        name='questionnaire_new'),
)

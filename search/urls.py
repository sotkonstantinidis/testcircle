from django.conf.urls import url, patterns

urlpatterns = patterns(
    '',
    url(r'^$', 'search.views.search', name='search'),
    url(r'^admin/$', 'search.views.admin', name='admin'),
    url(r'^update/(?P<configuration>\w+)/$', 'search.views.update',
        name='update'),
)

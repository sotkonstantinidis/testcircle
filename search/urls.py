from django.conf.urls import url, patterns

urlpatterns = patterns(
    '',
    url(r'^$', 'search.views.search', name='search'),
    url(r'^admin/$', 'search.views.admin', name='admin'),
    url(r'^delete/$', 'search.views.delete_all', name='delete_all'),
    url(r'^delete/(?P<configuration>\w+)/$', 'search.views.delete_one',
        name='delete_one'),
    url(r'^index/(?P<configuration>\w+)/$', 'search.views.index',
        name='index'),
    url(r'^update/(?P<configuration>\w+)/$', 'search.views.update',
        name='update'),
)

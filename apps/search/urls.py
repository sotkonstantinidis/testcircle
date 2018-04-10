from django.conf.urls import url, patterns

from configuration.views import BuildAllCachesView
from search.views import FilterValueView

urlpatterns = patterns(
    '',
    url(r'^$', 'search.views.search', name='search'),
    url(r'^admin/$', 'search.views.admin', name='admin'),
    url(r'^delete/$', 'search.views.delete_all', name='delete_all'),
    url(r'^delete/(?P<configuration>\w+)/(?P<edition>\w+)/$', 'search.views.delete_one',
        name='delete_one'),
    url(r'^index/(?P<configuration>\w+)/(?P<edition>\w+)/$', 'search.views.index',
        name='index'),
    url(r'^update/(?P<configuration>\w+)/(?P<edition>\w+)/$', 'search.views.update',
        name='update'),
    # This does not necessarily belong here
    url(r'^cache/delete/$', 'configuration.views.delete_caches',
        name='delete_caches'),
    url(r'^cache/build/$', BuildAllCachesView.as_view(), name='build_caches'),
    url(r'^value/$', FilterValueView.as_view(), name='filter_value'),
)

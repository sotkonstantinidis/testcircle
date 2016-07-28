from django.conf.urls import patterns, url

from .views import LogListView


urlpatterns = patterns(
    '',
    url(r'^$', LogListView.as_view(), name='notification_list'),
    url(r'^teaser/$', LogListView.as_view(is_teaser=True), name='notification_list_teaser'),
)

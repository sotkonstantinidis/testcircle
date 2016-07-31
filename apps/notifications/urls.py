from django.conf.urls import patterns, url

from .views import LogListView, LogListTeaserView, ReadLogUpdateView


urlpatterns = patterns(
    '',
    url(r'^$', LogListView.as_view(), name='notification_list'),
    url(r'^teaser/$', LogListTeaserView.as_view(), name='notification_list_teaser'),
    url(r'^read/$', ReadLogUpdateView.as_view(), name='notification_read'),
)

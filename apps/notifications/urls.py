from django.conf.urls import patterns, url

from .views import LogListView


urlpatterns = patterns(
    '',
    url(r'^list/$', LogListView.as_view(), name='notification_list'),
)

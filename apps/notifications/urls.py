from django.conf.urls import patterns, url

from .views import LogListView, LogListTeaserView, ReadLogUpdateView


urlpatterns = patterns(
    '',
    url(r'^$', LogListView.as_view(), name='notification_list'),
    url(r'^todo/$', LogListView.as_view(queryset_method='user_action_list'), name='workflow_todo_list'),
    url(r'^teaser/all/$', LogListTeaserView.as_view(), name='notification_list_teaser'),
    url(r'^teaser/todo/$',
        LogListTeaserView.as_view(queryset_method='user_action_list'),  name='workflow_todo_list_teaser'
        ),
    url(r'^read/$', ReadLogUpdateView.as_view(), name='notification_read'),
)

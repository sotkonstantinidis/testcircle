from django.conf.urls import patterns, url
from django.views.generic import TemplateView

from .views import LogListView, ReadLogUpdateView, LogCountView


urlpatterns = patterns(
    '',
    url(r'^$',
        TemplateView.as_view(template_name='notifications/log_list.html'),
        name='notification_list'
        ),
    url(r'^partial/$',
        LogListView.as_view(),
        name='notification_partial_list'
        ),
    url(r'^read/$',
        ReadLogUpdateView.as_view(),
        name='notification_read'
        ),
    url(r'^new-notifications/$',
        LogCountView.as_view(),
        name='notification_new_count'
        ),
)

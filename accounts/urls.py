"""
This module contains the URL routing patterns for the :mod:`accounts`
app.
"""
from django.conf.urls import patterns, url

urlpatterns = patterns(
    '',
    url(r'^login$', 'accounts.views.login', name='login'),
    url(r'^logout$', 'accounts.views.logout', name='logout'),
    url(r'^welcome$', 'accounts.views.welcome', name='welcome'),
    url(r'^search$', 'accounts.views.user_search', name='user_search'),
    url(r'^update$', 'accounts.views.user_update', name='user_update'),
    url(r'^user/(?P<id>\d+)$', 'accounts.views.details', name='user_details'),
)

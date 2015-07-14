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
)

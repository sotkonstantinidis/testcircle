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
    url(r'^(?P<user_id>[0-9]+)/questionnaires$',
        'accounts.views.questionnaires', name='account_questionnaires'),
    url(r'^moderation$', 'accounts.views.moderation',
        name='account_moderation'),
)

from django.conf.urls import url, patterns

urlpatterns = patterns(
    '',
    url(r'^upload/$', 'questionnaire.views.generic_file_upload',
        name='file_upload'),
    url(r'^file/(?P<action>\w+)/(?P<uid>[^/]+)/$',
        'questionnaire.views.generic_file_serve', name='file_serve'),
)

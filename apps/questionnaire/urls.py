from django.conf.urls import url, patterns

from questionnaire.views import QuestionnaireDeleteView

urlpatterns = patterns(
    '',
    url(r'^upload/$', 'questionnaire.views.generic_file_upload',
        name='file_upload'),
    url(r'^file/(?P<action>\w+)/(?P<uid>[^/]+)/$',
        'questionnaire.views.generic_file_serve', name='file_serve'),
    url(r'^edit/(?P<identifier>[^/]+)/delete/$',
        QuestionnaireDeleteView.as_view(),
        name='delete_questionnaire')
)

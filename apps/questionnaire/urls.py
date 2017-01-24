from django.conf.urls import url, patterns

from questionnaire.views import QuestionnaireLockView, \
    QuestionnaireSummaryPDFCreateView

urlpatterns = patterns(
    '',
    url(r'^upload/$', 'questionnaire.views.generic_file_upload',
        name='file_upload'),
    url(r'^file/(?P<action>\w+)/(?P<uid>[^/]+)/$',
        'questionnaire.views.generic_file_serve', name='file_serve'),
    url(r'^edit/(?P<identifier>[^/]+)/lock/$',
        QuestionnaireLockView.as_view(),
        name='lock_questionnaire'),
    url(r'^view/(?P<id>[\d]+)/summary/$',
        QuestionnaireSummaryPDFCreateView.as_view(),
        name='questionnaire_summary'),
)

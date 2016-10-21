from django.conf.urls import url, patterns

from .views import QuestionnaireDeleteView, QuestionnaireSummaryExportView, \
    QuestionnaireSummaryPDFCreateView

urlpatterns = patterns(
    '',
    url(r'^upload/$', 'questionnaire.views.generic_file_upload',
        name='file_upload'),
    url(r'^file/(?P<action>\w+)/(?P<uid>[^/]+)/$',
        'questionnaire.views.generic_file_serve', name='file_serve'),
    url(r'^edit/(?P<identifier>[^/]+)/delete/$',
        QuestionnaireDeleteView.as_view(),
        name='delete_questionnaire'),
    url(r'^view/(?P<identifier>[^/]+)/summary/$',
        QuestionnaireSummaryExportView.as_view(),
        name='export_questionnaire_summary'),
    url(r'^view/(?P<identifier>[^/]+)/summary/pdf$',
        QuestionnaireSummaryPDFCreateView.as_view(),
        name='pdf_questionnaire_summary')
)

from django.conf.urls import url, patterns

from questionnaire.forms import QUESTIONNAIRES_LIST
from questionnaire.views import QuestionnaireWizard


questionnaireWizard = QuestionnaireWizard.as_view(
    QUESTIONNAIRES_LIST, url_name='questionnaire_new_step')

urlpatterns = patterns(
    '',
    url(r'^new/(?P<step>.+)/$', questionnaireWizard,
        name='questionnaire_new_step'),
    url(r'^new/$', questionnaireWizard, name='questionnaire_new'),
)

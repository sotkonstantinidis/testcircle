from django.conf.urls import url

from questionnaire.forms import QUESTIONNAIRES_LIST
from questionnaire.views import QuestionnaireWizard

urlpatterns = [
    url(r'^new/$', QuestionnaireWizard.as_view(QUESTIONNAIRES_LIST),
        name='questionnaire_new'),
]

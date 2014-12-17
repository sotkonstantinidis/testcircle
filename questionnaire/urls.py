from django.conf.urls import url, patterns

from questionnaire.views import QuestionnaireWizard
from questionnaire.config.base import BaseConfig
baseConfig = BaseConfig()

questionnaireWizard = QuestionnaireWizard.as_view(
    baseConfig.getFormList(), url_name='questionnaire_new_step')

urlpatterns = patterns(
    '',
    url(r'^new/(?P<step>.+)/$', questionnaireWizard,
        name='questionnaire_new_step'),
    # url(r'^new/$', questionnaireWizard, name='questionnaire_new'),
    url(r'^view/(\d+)/$', 'questionnaire.views.questionnaire_view',
        name='questionnaire_view'),
    url(r'^new/$', 'questionnaire.views.questionnaire_new',
        name='questionnaire_new'),
)

from django.contrib.auth import get_user_model
from django.core.urlresolvers import reverse
from model_mommy import mommy
from questionnaire.models import Questionnaire, QuestionnaireMembership

from functional_tests.base import FunctionalTest


class NotificationsIntegrationTest(FunctionalTest):
    """
    Specific tests for triggering and displaying of notifications

    jay is a compiler
    robin is an editor
    """
    fixtures = ['sample_global_key_values', 'sample', 'sample_questionnaires']

    def setUp(self):
        super().setUp()
        self.jay = mommy.make(get_user_model())
        self.robin = mommy.make(get_user_model())
        self.questionnaire = Questionnaire.objects.first()
        mommy.make(
            model=QuestionnaireMembership,
            user=self.jay,
            questionnaire=self.questionnaire,
            role='compiler'
        )
        mommy.make(
            model=QuestionnaireMembership,
            user=self.robin,
            questionnaire=self.questionnaire,
            role='editor'
        )
        self.notifications_url = '{}{}'.format(
            self.live_server_url,
            reverse('notification_list')
        )
        self.questionnaire_edit_url = '{}{}'.format(
            self.live_server_url,
            self.questionnaire.get_edit_url()
        )

    def test_editor_finished(self):
        # when jay edits the questionnaire, the 'finish edit' button is not
        # shown
        self.doLogin(self.jay)
        self.browser.get(self.questionnaire_edit_url)
        self.findBy('id', 'confirm-submit')
        self.findByNot('id', 'finish-editing')
        # todo: fix problems with doLogin

from unittest.mock import patch

from accounts.client import Typo3Client
from configuration.models import Configuration
from django.conf import settings
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
        self.jay = mommy.make(
            get_user_model(),
            firstname='jay'
        )
        self.robin = mommy.make(
            get_user_model(),
            firstname='robin'
        )
        self.questionnaire = mommy.make(
            model=Questionnaire,
            status=settings.QUESTIONNAIRE_DRAFT,
            configurations=[Configuration.objects.filter(
                code='technology', active=True
            ).first()]
        )
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

    def test_compiler_edit_questionnaire(self):
        # The compiler logs in and doesn't see the button to finish editing.
        self.doLogin(user=self.jay)
        self.browser.get(self.questionnaire_edit_url)

        self.findBy('id', 'confirm-submit')
        self.findByNot('id', 'finish-editing')

    def test_create_message(self):
        pass

from accounts.models import User
from questionnaire.models import Questionnaire

from .models import Log, StatusUpdate, ContentUpdate


class CreateLog:
    """
    Create a new log an set the required instance variables for status and content updates.
    """

    def __init__(self, action: int, sender: User, questionnaire: Questionnaire, **kwargs):
        self.log = self.create_log(sender, action, questionnaire)
        self.questionnaire = questionnaire
        self.message = kwargs.get('message', '')

    def create_log(self, sender, action, questionnaire):
        log = Log.objects.create(
            catalyst=sender,
            action=action,
            questionnaire=questionnaire
        )
        # Add current members as receivers.
        members = questionnaire.questionnairemembership_set.exclude(
            user=sender
        ).values_list(
            'user_id', flat=True
        )
        log.subscribers.add(*members)
        return log


class StatusLog(CreateLog):

    def create(self):
        StatusUpdate.objects.create(
            log=self.log,
            status=self.questionnaire.status,
            message=self.message
        )


class ContentLog(CreateLog):

    def create(self):
        ContentUpdate.objects.create(
            log=self.log,
            data=self.questionnaire.data
        )

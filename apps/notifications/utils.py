from accounts.models import User
from questionnaire.models import Questionnaire

from .models import Log, StatusUpdate, ContentUpdate, MemberUpdate


class CreateLog:
    """
    Create a new log an set the required instance variables for status and content updates.
    """
    def __init__(self, action: int, sender: User, questionnaire: Questionnaire, **kwargs):
        self.log = self.create_log(sender, action, questionnaire)
        self.questionnaire = questionnaire

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


class ContentLog(CreateLog):
    """
    Helper to create logs for changed questionnaire data.
    """
    def create(self):
        ContentUpdate.objects.create(
            log=self.log,
            data=self.questionnaire.data
        )


class StatusLog(CreateLog):
    """
    Helper to create logs for changed review cycle status.
    """
    def create(self):
        StatusUpdate.objects.create(
            log=self.log,
            status=self.questionnaire.status
        )


class MemberLog(CreateLog):
    """
    Helper to create logs for changed questionnaire membership.
    """
    def create(self, affected: User, role: str):
        MemberUpdate.objects.create(
            log=self.log,
            affected=affected,
            role=role
        )

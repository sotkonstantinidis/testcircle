from django.dispatch import receiver

from accounts.models import User
from questionnaire.models import Questionnaire
from questionnaire import signals

from .conf import settings
from .utils import StatusLog, ContentLog


@receiver(signals.change_status)
def create_status_notification(sender: int, questionnaire: Questionnaire, reviewer: User, **kwargs):
    StatusLog(action=sender, sender=reviewer, questionnaire=questionnaire, **kwargs).create()


@receiver(signals.change_member)
def modify_member(sender: int, questionnaire: Questionnaire, reviewer: User, person: User, role: str, **kwargs):
    """
    Put together a message ('add / delete member') and store the log.
    """
    message = '{reviewer} {action} "{person}" as {role}'.format(
        reviewer=reviewer,
        action=dict(settings.NOTIFICATIONS_ACTIONS).get(sender),
        person=person,
        role=role
    )
    StatusLog(action=sender, sender=reviewer, questionnaire=questionnaire, message=message).create()


@receiver(signals.create_questionnaire)
def create_questionnaire(sender: int, questionnaire: Questionnaire, reviewer: User, **kwargs):
    StatusLog(action=sender, sender=reviewer, questionnaire=questionnaire, **kwargs).create()


@receiver(signals.delete_questionnaire)
def delete_questionnaire(sender: int, questionnaire: Questionnaire, reviewer: User, **kwargs):
    StatusLog(action=sender, sender=reviewer, questionnaire=questionnaire, **kwargs).create()


@receiver(signals.change_questionnaire_data)
def change_questionnaire_data(sender: int, questionnaire: Questionnaire, user: User, **kwargs):
    ContentLog(action=sender, sender=user, questionnaire=questionnaire).create()

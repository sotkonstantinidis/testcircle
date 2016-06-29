from django.dispatch import receiver

from accounts.models import User
from notifications.models import Message
from questionnaire.models import Questionnaire

from questionnaire.signals import create_questionnaire, delete_questionnaire, change_member, change_status


@receiver(change_status)
def create_status_notification(sender: str, questionnaire: Questionnaire, reviewer: User, **kwargs):
    CreateMessage(action=sender, sender=reviewer, questionnaire=questionnaire, **kwargs)


@receiver(change_member)
def modify_member(sender: str, questionnaire: Questionnaire, reviewer: User, person: User, role: str, **kwargs):
    message = '{person} ({role})'.format(person=person, role=role)
    CreateMessage(action=sender, sender=reviewer, questionnaire=questionnaire, message=message)


@receiver(create_questionnaire)
def create_questionnaire(sender: int, questionnaire: Questionnaire, reviewer: User, **kwargs):
    CreateMessage(action=sender, sender=reviewer, questionnaire=questionnaire, **kwargs)


@receiver(delete_questionnaire)
def delete_questionnaire(sender: str, questionnaire: Questionnaire, reviewer: User, **kwargs):
    CreateMessage(action=sender, sender=reviewer, questionnaire=questionnaire, **kwargs)


class CreateMessage:
    """
    Create a new notification if the status has changed (=no notification exists).
    Note: this only works properly if called synchronously. Receivers may change in time.

    """
    def __init__(self, action, sender, questionnaire, **kwargs):
        message = Message.objects.create(
            sender=sender,
            action=action,
            questionnaire=questionnaire,
            status=questionnaire.status,
            message=kwargs.get('message', '')
        )
        # Add current members as receivers.
        members = questionnaire.questionnairemembership_set.exclude(
            user=sender
        ).values_list(
            'user_id', flat=True
        )
        message.receivers.add(*members)
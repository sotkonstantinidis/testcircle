from django.db import models

from accounts.models import User
from questionnaire.models import Questionnaire, STATUSES

from .conf import settings


class Message(models.Model):
    """
    Represent a single message. Used to send mails, display messages on the frontend and get a history of changes
    for a questionnaire.

    """
    created = models.DateTimeField(auto_now_add=True)
    sender = models.ForeignKey(User, related_name='sender')
    receivers = models.ManyToManyField(User, related_name='receivers')
    questionnaire = models.ForeignKey(Questionnaire)
    action = models.PositiveIntegerField(choices=settings.NOTIFICATIONS_ACTIONS)
    status = models.PositiveIntegerField(choices=STATUSES, null=True, blank=True)
    message = models.TextField()
    # finished = models.DateTimeField(null=True, blank=True) --> add this as soon as we send mails.

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return '{action}: {questionnaire} ({status})'.format(
            action=self.action,
            questionnaire=self.questionnaire.code,
            status=self.get_status_display()
        )
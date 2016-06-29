from django.db import models

from accounts.models import User
from questionnaire.models import Questionnaire, STATUSES


class Message(models.Model):
    """
    Represent a single message. Used to send mails, display messages on the frontend and get a history of changes
    for a questionnaire.

    """
    sender = models.ForeignKey(User, related_name='sender')
    receivers = models.ManyToManyField(User, related_name='receivers')
    questionnaire = models.ForeignKey(Questionnaire)
    status = models.CharField(choices=STATUSES, max_length=10)
    created = models.DateTimeField(auto_now_add=True)
    finished = models.DateTimeField(null=True, blank=True)

    class Meta:
        ordering = ['created']

    def __str__(self):
        return '{self.questionnaire}: {self.status}'.format(self=self)
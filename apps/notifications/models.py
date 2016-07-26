# -*- coding: utf-8 -*-
import contextlib

from django.db import models
from django.utils.translation import ugettext_lazy as _

from accounts.models import User
from django.utils.functional import cached_property
from django_pgjson.fields import JsonBField
from questionnaire.models import Questionnaire, STATUSES

from .conf import settings


class Log(models.Model):
    """
    Represent a change of the questionnaire. This may be an update of the content or a change in the status.
    New logs should be created only by the receivers only.

    If the triggering action is a status change, a StatusUpdate is created.
    If the triggering action is a content change, a ContentUpdate is created.

    These models are structured in this way that:
    - emails can be sent easily (sender, receivers, subject, message are available)
    - all logs for a questionnaire can be found easily (Log.objects.filter(questionnaire__code='foo')
    - all logs for a user can be found easily

    Dividing StatusUpdate and ContentUpdate is a heuristic choice in order to prevent many empty cells on the db. It is
    expected that more ContentUpdates are created.

    """
    created = models.DateTimeField(auto_now_add=True)
    catalyst = models.ForeignKey(User, related_name='catalyst', help_text='Person triggering the log')
    subscribers = models.ManyToManyField(
        User, related_name='subscribers', help_text='All people that are members of the questionnaire'
    )
    questionnaire = models.ForeignKey(Questionnaire)
    action = models.PositiveIntegerField(choices=settings.NOTIFICATIONS_ACTIONS)

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return self.subject

    @cached_property
    def subject(self) -> str:
        """
        Fetch the subject from the related model depending on the action.
        """
        if self.is_content_update:
            return _('{person} edited the questionnaire {code}'.format(
                person=self.catalyst.get_display_name(), code=self.questionnaire.code
            ))
        else:
            return _('{questionnaire} has a new status: {status}'.format(
                questionnaire=self.questionnaire.code, status=self.statusupdate.get_status_display()
            ))

    @cached_property
    def message(self) -> str:
        """
        Fetch the message from the related model depending on the action.
        """
        return self.contentupdate.difference if self.is_content_update else self.statusupdate.message

    @cached_property
    def is_content_update(self):
        return self.action is settings.NOTIFICATIONS_EDIT_CONTENT


class StatusUpdate(models.Model):
    """
    Store the status of the questionnaire in the moment that the log is created for all changes regarding the
    publication cycle.

    """
    log = models.OneToOneField(Log)
    status = models.PositiveIntegerField(choices=STATUSES, null=True, blank=True)
    message = models.TextField()


class ContentUpdate(models.Model):
    """
    Store the previous questionnaire data.

    """
    log = models.OneToOneField(Log)
    data = JsonBField()

    def difference(self) -> dict:
        with contextlib.suppress(Log.DoesNotExist):
            previous = self.log.get_previous_by_created(contentupdate__isnull=False)
            # calculate diff here.
            return self.data
        return {}

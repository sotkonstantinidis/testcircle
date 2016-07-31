# -*- coding: utf-8 -*-
import contextlib
import functools
import operator

from django.db import models
from django.db.models import Q
from django.template.loader import render_to_string
from django.utils.translation import ugettext_lazy as _
from django.utils.functional import cached_property

from django_pgjson.fields import JsonBField
from accounts.models import User
from questionnaire.models import Questionnaire, STATUSES

from .conf import settings


class ActionContextQuerySet(models.QuerySet):
    """
    Filters actions according to context. E.g. get actions for my profile notifications, get actions for emails.
    """
    def get_questionnaires_for_permissions(self, *user_permissions) -> list:
        """
        Create filters for questionnaire statuses according to permissions.
        """
        filters = []
        for permission, status in settings.NOTIFICATIONS_QUESTIONNAIRE_STATUS_PERMISSIONS.items():
            if permission in user_permissions:
                filters.append(
                    Q(questionnaire__status=status, action=settings.NOTIFICATIONS_CHANGE_STATUS)
                )
        return filters

    def user_log_list(self, user: User):
        """
        Fetch all logs where given user is
        - either catalyst or subscriber of the log (set the moment the log was created)
        - permitted to see the log as defined by the role.
        """
        # construct filters depending on the users permissions.
        status_filters = self.get_questionnaires_for_permissions(*user.get_all_permissions())
        # extend basic filters according to catalyst / subscriber
        status_filters.extend([Q(subscribers=user), Q(catalyst=user)])

        return self.filter(
            action__in=settings.NOTIFICATIONS_USER_PROFILE_ACTIONS
        ).filter(
            functools.reduce(operator.or_, status_filters)
        ).distinct()

    def email(self):
        return self.filter(action__in=settings.NOTIFICATIONS_EMAIL_ACTIONS)


class Log(models.Model):
    """
    Represent a change of the questionnaire. This may be an update of the content or a change in the status.
    New logs should be created only by the receivers only.

    If the triggering action is a status change, a StatusUpdate is created.
    If the triggering action is a content change, a ContentUpdate is created.
    If the triggering action is a membership change, a MemberUpdate is created.

    These models are structured in this way that:
    - emails can be sent easily (sender, receivers, subject, message are available)
    - all logs for a questionnaire can be found easily (Log.objects.filter(questionnaire__code='foo')
    - all logs for a user can be found easily

    Dividing StatusUpdate, MemberUpdate and ContentUpdate is a heuristic choice in order to prevent many empty cells
    on the db. It is expected that more ContentUpdates are created.

    """
    created = models.DateTimeField(auto_now_add=True)
    catalyst = models.ForeignKey(User, related_name='catalyst', help_text='Person triggering the log')
    subscribers = models.ManyToManyField(
        User, related_name='subscribers', help_text='All people that are members of the questionnaire'
    )
    questionnaire = models.ForeignKey(Questionnaire)
    action = models.PositiveIntegerField(choices=settings.NOTIFICATIONS_ACTIONS)

    objects = models.Manager()
    actions = ActionContextQuerySet.as_manager()

    class Meta:
        ordering = ['-created']

    def __str__(self):
        return '{questionnaire}: {action}'.format(
            questionnaire=self.questionnaire.code,
            action=self.get_action_display()
        )

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
            # todo: this is not always correct - member changes. fix this as soon as this method is used to send mails.
            return _('{questionnaire} has a new status: {status}'.format(
                questionnaire=self.questionnaire.code, status=self.statusupdate.get_status_display()
            ))

    def message(self, user: User) -> str:
        """
        Fetch the message from the related model depending on the action.
        """
        return self.contentupdate.difference if self.is_content_update else self.get_linked_subject(user)

    @cached_property
    def is_content_update(self) -> bool:
        return self.action is settings.NOTIFICATIONS_EDIT_CONTENT

    def get_linked_subject(self, user: User) -> str:
        """
        The subject with links to questionnaire and catalyst, according to the type of the action.
        Use the integer as template name, as this value is fixed (opposed to the verbose name).
        """
        if self.action in settings.NOTIFICATIONS_USER_PROFILE_ACTIONS:
            return render_to_string('notifications/subject/{}.html'.format(self.action), {'log': self, 'user': user})


class StatusUpdate(models.Model):
    """
    Store the status of the questionnaire in the moment that the log is created for all changes regarding the
    publication cycle.

    """
    log = models.OneToOneField(Log)
    status = models.PositiveIntegerField(choices=STATUSES, null=True, blank=True)


class MemberUpdate(models.Model):
    """
    Invited or removed members.
    """
    log = models.OneToOneField(Log)
    affected = models.ForeignKey(User)
    role = models.CharField(max_length=50)


class ContentUpdate(models.Model):
    """
    Store the previous questionnaires data.
    """
    log = models.OneToOneField(Log)
    data = JsonBField()

    def difference(self) -> dict:
        """
        If the selected package provides consistent results, we may store the diff only. Until then, store the whole
        data and calculate the diff when required.
        """
        with contextlib.suppress(Log.DoesNotExist):
            previous = self.log.get_previous_by_created(contentupdate__isnull=False)
            # calculate diff here.
            return self.data
        return {}


class ReadLog(models.Model):
    """
    Store the 'is_done' state for each user. This is more or less equivalent to the 'read' state in any email program.
    This can't be handled in the 'through' model of the subscriber, as the status must also be stored for the catalyst.
    """
    log = models.ForeignKey(Log, on_delete=models.PROTECT)
    user = models.ForeignKey(User, on_delete=models.PROTECT)
    is_read = models.BooleanField(default=False)

    class Meta:
        # only one read status per user and log, preventing a race condition.
        unique_together = ['log', 'user']

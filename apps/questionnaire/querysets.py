from datetime import timedelta
from django.db import models
from django.db.models import Q
from django.utils.timezone import now

from .conf import settings


class StatusQuerySet(models.QuerySet):
    """
    Helper for verbose queries. Use as:
    Questionnaire.with_status.published()
    """

    def public(self):
        return self.filter(status=settings.QUESTIONNAIRE_PUBLIC)

    def draft(self):
        return self.filter(status=settings.QUESTIONNAIRE_DRAFT)

    def not_deleted(self):
        return self.filter(is_deleted=False)


class LockStatusQuerySet(models.QuerySet):
    """
    Helpers to get locked / unlocked Questionnaires
    """

    @property
    def expired(self):
        # Get latest time in which locks are still valid
        return now() - timedelta(minutes=settings.QUESTIONNAIRE_LOCK_TIME)

    def is_blocked(self):
        return self.filter(
            Q(is_finished=False), Q(start__gte=self.expired)
        )

    def is_editable(self):
        return self.filter(
            Q(is_finished=True) | Q(start__lte=self.expired)
        )

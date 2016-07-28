from typing import Iterable

from django.db.models import Q
from django.views.generic import ListView
from django.conf import settings

from braces.views import LoginRequiredMixin

from .models import Log


class LogListView(LoginRequiredMixin, ListView):
    """
    Display logs which the current user is a reciepient of.
    """
    template_name = 'notifications/log_list.html'
    context_object_name = 'logs'
    is_teaser = None

    def add_user_aware_data(self, logs: list) -> Iterable:
        """
        The method 'get_linked_subject' requires a user. Provide all info required for the template.
        """
        for log in logs:
            yield {
                'id': log.id,
                'created': log.created,
                'text': log.get_linked_subject(user=self.request.user)
            }

    def get_queryset(self) -> Iterable:
        """
        Fetch notifications for the current user.
        """
        logs = Log.actions.my_profile().filter(
            Q(subscribers=self.request.user) | Q(catalyst=self.request.user)
        )
        if self.is_teaser:
            logs = logs[:settings.NOTIFICATIONS_TEASER_SLICE]
        return self.add_user_aware_data(logs=logs)

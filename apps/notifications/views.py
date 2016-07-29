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
    context_object_name = 'logs'
    template_name = 'notifications/log_list.html'
    paginate_by = settings.NOTIFICATIONS_LIST_PAGINATE_BY

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

    def get_logs(self):
        """
        Use own method, so the teaser view can slice the queryset.
        """
        return Log.actions.my_profile().filter(
            Q(subscribers=self.request.user) | Q(catalyst=self.request.user)
        )

    def get_queryset(self) -> list:
        """
        Fetch notifications for the current user.
        """
        return list(self.add_user_aware_data(logs=self.get_logs()))


class LogListTeaserView(LogListView):
    """
    Get only a small number of notifications without pagination to display on the 'My SLM data' page.
    """
    template_name = 'notifications/partial/list.html'
    paginate_by = 0

    def get_logs(self):
        return super().get_logs()[:settings.NOTIFICATIONS_TEASER_SLICE]

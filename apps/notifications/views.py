from typing import Iterable

from django.views.generic import ListView

from braces.views import LoginRequiredMixin

from .models import Log


class LogListView(LoginRequiredMixin, ListView):
    """
    Display logs which the current user is a reciepient of.
    """
    template_name = 'notifications/log_list.html'
    context_object_name = 'logs'

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
        # .filter(subscribers=self.request.user)
        return self.add_user_aware_data(logs=Log.actions.my_profile())

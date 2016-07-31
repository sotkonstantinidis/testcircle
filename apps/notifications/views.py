import logging
from typing import Iterable

from django.db.models import Q
from django.http import Http404
from django.http import HttpResponse
from django.views.generic import ListView
from django.conf import settings

from braces.views import LoginRequiredMixin
from django.views.generic import View

from .models import Log, ReadLog


logger = logging.getLogger(__name__)


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
                'text': log.get_linked_subject(user=self.request.user),
                'is_read': log.readlog_set.filter(user=self.request.user, is_read=True).exists()
            }

    def get_logs(self):
        """
        Use own method, so the teaser view can slice the queryset.
        """
        return Log.actions.my_profile(user=self.request.user)

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


class ReadLogUpdateView(LoginRequiredMixin, View):
    """
    Update the 'is_read' flag for a log.
    """
    http_method_names = ['post']

    def validate_data(self, **kwargs) -> bool:
        """
        Validate required keys and user from the request.
        """
        if not all([key in ['checked', 'log', 'user'] for key in kwargs.keys()]):
            return False
        try:
            user_id = int(kwargs['user'])
        except ValueError:
            return False
        if user_id != self.request.user.id:
            return False
        return True

    def post(self, request, *args, **kwargs):
        """
        Validate post data and create/update the readlog.
        """
        data = request.POST.dict()
        is_valid = self.validate_data(**data)
        if is_valid:
            ReadLog.objects.update_or_create(
                user_id=data['user'], log_id=data['log'],
                defaults={'is_read': True if data['checked'] == 'true' else False}
            )
            return HttpResponse(status=200)
        else:
            logging.error('Invalid attempt to update a ReadLog (data: {})'.format(data))
            raise Http404()

import logging
from typing import Iterable

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
    queryset_method = 'user_log_list'

    def get_log_ids(self, logs) -> list:
        """
        Returns a list with all ids for given logs. Used to filter the readlogs.
        """
        return logs.values_list('id', flat=True)

    def get_readlog_list(self, logs) -> list:
        """
        Create a list with all log_ids that are 'read' for the current user. By creating this list, the db is hit only
        once instead of n (paginate_by) times.
        """
        return ReadLog.objects.only(
            'log__id'
        ).filter(
            log__id__in=self.get_log_ids(logs), user=self.request.user, is_read=True
        ).values_list(
            'log__id', flat=True
        )

    def get_is_todo(self, status: int, action: int) -> bool:
        """
        For all actions that are a status change, check if current user has permissions to handle the questionnaire.
        """
        return action is settings.NOTIFICATIONS_CHANGE_STATUS and status in self.todo_statuses

    def add_user_aware_data(self, logs) -> Iterable:
        """
        The method 'get_linked_subject' requires a user. Provide all info required for the template.
        """
        readlog_list = self.get_readlog_list(logs=logs)
        # A list with all statuses that the current user is allowed to handle.
        self.todo_statuses = [
            status for permission, status in settings.NOTIFICATIONS_QUESTIONNAIRE_STATUS_PERMISSIONS.items()
            if permission in self.request.user.get_all_permissions()
            ]

        for log in logs:
            yield {
                'id': log.id,
                'created': log.created,
                'text': log.get_linked_subject(user=self.request.user),
                'is_read': log.id in readlog_list,
                'is_todo': self.get_is_todo(status=log.questionnaire.status, action=log.action)
            }

    def get_logs(self):
        """
        Use own method (not get_queryset), so the teaser view can slice the queryset.
        """
        return Log.actions.user_log_list(user=self.request.user)

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

    def get_log_ids(self, logs) -> list:
        return [log.id for log in logs]

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

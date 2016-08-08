import logging
from typing import Iterable

from django.conf import settings
from django.http import Http404
from django.http import HttpResponse
from django.views.generic import ListView, View

from braces.views import LoginRequiredMixin
from qcat.utils import url_with_querystring

from .models import Log, ReadLog


logger = logging.getLogger(__name__)


class LogListView(LoginRequiredMixin, ListView):
    """
    Display logs for the current user.

    This view accepts following parameters as get-querystrings:
    - page (default django pagination)
    - is_teaser: smaller pagination size
    - is_pending: only logs that are 'to do' for the user

    """
    template_name = 'notifications/partial/list.html'

    def get_is_todo(self, status: int, action: int, log_status: int) -> bool:
        """
        For all actions that are a status change, check if current user has
        permissions to handle the questionnaire and the questionnaires status
        is still the same as when the log was created (=no one reviewed the
        questionnaire).
        """
        return action is settings.NOTIFICATIONS_CHANGE_STATUS and status is log_status and status in self.todo_statuses

    def add_user_aware_data(self, logs) -> Iterable:
        """
        Provide all info required for the template, so as little logic as
        possible is required within the template.
        """
        # All logs with the status 'read' for the logs on display.
        readlog_list = Log.actions.read_ids(
            user=self.request.user,
            log_id__in=list(logs.values_list('id', flat=True))
        )

        # A list with all logs that are pending for the user
        pending_questionnaires = Log.actions.user_pending_list(
            user=self.request.user
        ).values_list(
            'id', flat=True
        )

        for log in logs:
            is_read = log.id in readlog_list
            # if a notification is read, it is assumed that it is resolved.
            is_todo = not is_read and log.id in pending_questionnaires
            yield {
                'id': log.id,
                'created': log.created,
                'text': log.get_linked_subject(user=self.request.user),
                'is_read': is_read,
                'is_todo': is_todo,
                'edit_url': log.questionnaire.get_edit_url() if is_todo else ''
            }

    @property
    def queryset_method(self):
        """
        Get the proper method name according to the GET request.
        """
        return 'user_pending_list' if 'is_pending' in self.request.GET.keys() else 'user_log_list'

    def get_paginate_by(self, queryset) -> int:
        """
        Return the setting variable according to the GET querystring.
        """
        return getattr(settings, 'NOTIFICATIONS_{}_PAGINATE_BY'.format(
            'TEASER' if 'is_teaser' in self.request.GET.keys() else 'LIST'
        ))

    def get_queryset(self):
        """
        Fetch notifications for the current user. Use the method as defined by
        the instance variable.
        """
        return getattr(Log.actions, self.queryset_method)(user=self.request.user)

    def get_context_data(self, **kwargs):
        """
        Enrich the paginated queryset with values as required by the template.
        Provide the 'path' with the same querystring as provided, plus 'page='.
        """
        context = super().get_context_data(**kwargs)
        context['logs'] = self.add_user_aware_data(context['object_list'])

        get_params = {}
        if 'is_teaser' in self.request.GET.keys():
            get_params['is_teaser'] = True
        if 'is_pending' in self.request.GET.keys():
            get_params['is_pending'] = True
        context['path'] = '{path}{symbol}page='.format(
            path=url_with_querystring(self.request.path, **get_params),
            symbol='&' if get_params else ''
        )
        return context


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
            logging.error('Invalid attempt to update a ReadLog '
                          '(data: {})'.format(data))
            raise Http404()


class LogCountView(View):
    """
    Get the current number of 'pending' notifications for the current user.
    Used to display the indicator with
    number next to the username in the menu.
    """
    http_method_names = ['get']

    def get(self, request, *args, **kwargs):
        return HttpResponse(
            content=Log.actions.user_log_count(user=self.request.user)
        )

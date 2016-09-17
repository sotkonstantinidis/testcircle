import logging
from typing import Iterable

from django.conf import settings
from django.core.urlresolvers import reverse
from django.http import Http404
from django.http import HttpResponse
from django.utils.functional import cached_property
from django.views.generic import ListView, TemplateView, View

from braces.views import LoginRequiredMixin
from qcat.utils import url_with_querystring

from .models import Log, ReadLog


logger = logging.getLogger(__name__)


class GetQueryStringMixin:
    """
    Helper to build the proper url with all get-params.
    """

    @cached_property
    def requested_questionnaire(self):
        request_questionnaire = self.request.GET.get('questionnaire')
        has_permissions = Log.actions.has_permissions_for_questionnaire(
            user=self.request.user, questionnaire_code=request_questionnaire
        )
        if request_questionnaire and has_permissions:
            return request_questionnaire
        return None

    def get_querystring_with_params(self):
        get_params = {}
        if 'is_teaser' in self.request.GET.keys():
            get_params['is_teaser'] = True
        if 'is_pending' in self.request.GET.keys():
            get_params['is_pending'] = True
        if self.requested_questionnaire:
            get_params['questionnaire'] = self.requested_questionnaire

        return '{path}{symbol}page='.format(
            path=url_with_querystring(
                path=reverse('notification_partial_list'), **get_params
            ),
            symbol='&' if get_params else ''
        )


class LogListTemplateView(LoginRequiredMixin, GetQueryStringMixin, TemplateView):
    template_name='notifications/log_list.html'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['path'] = self.get_querystring_with_params()
        return context


class LogListView(LoginRequiredMixin, GetQueryStringMixin, ListView):
    """
    Display logs for the current user.

    This view accepts following parameters as get-querystrings:
    - page (default django pagination)
    - is_teaser: smaller pagination size
    - is_pending: only logs that are 'to do' for the user

    """
    template_name = 'notifications/partial/list.html'

    def add_user_aware_data(self, logs) -> Iterable:
        """
        Provide all info required for the template, so as little logic as
        possible is required within the template.
        """
        # All logs with the status 'read' for the logs on display.
        readlog_list = Log.actions.read_id_list(
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
                'subject': log.subject,
                'text': log.get_linked_subject(user=self.request.user),
                'action_icon': log.action_icon(),
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
        the instance variable. Filter according to questionnaire if requested.
        """
        qs = getattr(Log.actions, self.queryset_method)(user=self.request.user)
        if self.requested_questionnaire:
            qs = qs.filter(questionnaire__code=self.requested_questionnaire)
        return qs

    def get_context_data(self, **kwargs):
        """
        Enrich the paginated queryset with values as required by the template.
        Provide the 'path' with the same querystring as provided, plus 'page='.
        """
        context = super().get_context_data(**kwargs)
        context['logs'] = self.add_user_aware_data(context['object_list'])
        context['path'] = self.get_querystring_with_params()
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
        # lambda is a workaround to access the 'kwargs.keys()' scope.
        if not all((lambda keys=kwargs.keys():
                    [key in keys for key in ['checked', 'log', 'user']])()):
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


class LogCountView(LoginRequiredMixin, View):
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

# -*- coding: utf-8 -*-
from django.utils.translation import ugettext_lazy as _
from django.conf import settings  # noqa

from appconf import AppConf


class NotificationsConf(AppConf):
    CREATE = 1
    DELETE = 2
    CHANGE_STATUS = 3
    ADD_MEMBER = 4
    REMOVE_MEMBER = 5

    ACTIONS = (
        (CREATE, _('created questionnaire')),
        (DELETE, _('deleted questionnaire')),
        (CHANGE_STATUS, _('changed status')),
        (ADD_MEMBER, _('added member')),
        (REMOVE_MEMBER, _('removed member'))
    )
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
    EDIT_CONTENT = 6

    ACTIONS = (
        (CREATE, _('created questionnaire')),
        (DELETE, _('deleted questionnaire')),
        (CHANGE_STATUS, _('changed status')),
        (ADD_MEMBER, _('invited')),
        (REMOVE_MEMBER, _('removed')),
        (EDIT_CONTENT, _('edited content'))
    )

    # All actions that should be listed on 'my slm data' -> notifications
    USER_PROFILE_ACTIONS = [CREATE, DELETE, CHANGE_STATUS, ADD_MEMBER, REMOVE_MEMBER]

    # All actions that should trigger an email
    EMAIL_ACTIONS = [CHANGE_STATUS]

    TEASER_SLICE = 5

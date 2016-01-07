from django.conf import settings  # noqa
from appconf import AppConf


class AccountConf(AppConf):
    """
    Custom settings for the account module. Mainly settings required for
    the login on the remote system.
    """
    PID = 3
    LOGIN_TYPE = 'login'
    LOGIN_SUCCESS_URL = 'home'

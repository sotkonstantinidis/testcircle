from django.conf import settings
from appconf import AppConf


class AccountConf(AppConf):
    """
    Custom settings for the account module. Mainly settings required for
    the login on the remote system.
    """
    PID = 3
    LOGIN_TYPE = 'login'

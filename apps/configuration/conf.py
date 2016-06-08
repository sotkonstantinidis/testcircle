from django.conf import settings  # noqa
from appconf import AppConf


class ConfigurationConf(AppConf):
    """
    Custom settings for the configuration module.
    """
    # Value-User relations
    VALUEUSER_UNCCD = 'unccd_fp'

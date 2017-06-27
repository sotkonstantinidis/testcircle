from os.path import join

from .config.common import BaseSettings
from .config.mixins import CompressMixin, DevMixin, ProdMixin, OpBeatMixin,\
    SecurityMixin, LogMixin, TestMixin, AuthenticationFeatureSwitch


class DevDefaultSite(DevMixin, AuthenticationFeatureSwitch, BaseSettings):
    pass


class TestDefaultSite(TestMixin, DevDefaultSite):
    pass


class ProdDefaultSite(ProdMixin, CompressMixin, SecurityMixin, OpBeatMixin,
                      LogMixin, BaseSettings):
    """
    Settings for live and demo hosting.
    """
    pass


class ProdDevDefaultSite(AuthenticationFeatureSwitch, ProdDefaultSite):
    """
    Settings for qcat-dev hosting.
    """
    pass

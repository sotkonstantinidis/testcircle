from .config.common import BaseSettings
from .config.mixins import CompressMixin, DevMixin, OpBeatMixin, SentryMixin, \
    ProdMixin, SecurityMixin, LogMixin, TestMixin


class DevDefaultSite(DevMixin, BaseSettings):
    pass


class TestDefaultSite(TestMixin, DevDefaultSite):
    pass


class ProdDefaultSite(ProdMixin, CompressMixin, OpBeatMixin, SecurityMixin,
                      SentryMixin, LogMixin, BaseSettings):
    pass

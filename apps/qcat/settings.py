from .config.common import BaseSettings
from .config.mixins import CompressMixin, DevMixin, OpBeatMixin, ProdMixin, SecurityMixin, LogMixin, \
    TestMixin


class DevDefaultSite(DevMixin, TestMixin, BaseSettings):
    pass


class ProdDefaultSite(ProdMixin, CompressMixin, OpBeatMixin, SecurityMixin, LogMixin, BaseSettings):
    pass

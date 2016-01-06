from .config.common import BaseSettings
from .config.mixins import DevMixin, ProdMixin, OpBeatMixin, SecurityMixin


class DevDefaultSite(DevMixin, BaseSettings):
    pass


class ProdDefaultSite(ProdMixin, OpBeatMixin, SecurityMixin, BaseSettings):
    pass

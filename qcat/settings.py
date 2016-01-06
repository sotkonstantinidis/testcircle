from qcat.config.common import BaseSettings
from qcat.config.mixins import DevMixin, ProdMixin, OpBeatMixin


class DevDefaultSite(DevMixin, BaseSettings):
    pass


class ProdDefaultSite(ProdMixin, OpBeatMixin, BaseSettings):
    pass

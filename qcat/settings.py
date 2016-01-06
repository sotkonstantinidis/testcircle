from os.path import normpath, join
from qcat.config.common import BaseSettings
from qcat.config.mixins import DevMixin, ProdMixin


class DevDefaultSite(DevMixin, BaseSettings):
    pass


class ProdDefaultSite(ProdMixin, BaseSettings):
    pass


class StageDefaultSite(ProdDefaultSite):
    pass

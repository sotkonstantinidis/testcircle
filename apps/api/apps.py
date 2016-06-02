from django.apps import AppConfig


class APIConfig(AppConfig):
    name = 'api'
    verbose_name = 'API'

    def ready(self):
        from . import receivers  # noqa

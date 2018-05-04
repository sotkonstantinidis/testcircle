from django.core.management.base import BaseCommand

from configuration.cache import delete_configuration_cache
from configuration.models import Configuration


class Command(BaseCommand):
    """
    This command deletes all configuration caches.
    """
    def handle(self, **options):
        active_configurations = Configuration.objects.all()
        for configuration in active_configurations:
            delete_configuration_cache(configuration)

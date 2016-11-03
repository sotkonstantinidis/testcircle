from django.core.management.base import NoArgsCommand
from questionnaire.models import Lock


class Command(NoArgsCommand):
    """
    Purge stale locks.
    """
    def handle_noargs(self, **options):
        Lock.with_status.is_editable().delete()

from django.contrib.auth import get_user_model
from django.core.management.base import NoArgsCommand

from notifications.models import MailPreferences


class Command(NoArgsCommand):
    """
    Set default mailpreferences for existing users.
    """
    def handle_noargs(self, **options):
        for user in get_user_model().objects.all():
            MailPreferences(user=user).set_defaults()

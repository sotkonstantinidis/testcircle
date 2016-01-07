from django.core.management.base import NoArgsCommand
from django.core.management import call_command


class Command(NoArgsCommand):
    """
    This Command handles the creation of the static initial values of
    QCAT, namely:

    * Create groups and permissions as found in
      ``accounts.fixtures.group_permissions.json``.

    Usage::
        (env)$ python3 manage.py load_qcat_data

    .. warning::
        Running this command will erase existing content in the given
        tables and insert new data. Handle with care!
    """
    def handle_noargs(self, **options):

        call_command('loaddata', 'groups_permissions')
        call_command('loaddata', 'global_key_values')

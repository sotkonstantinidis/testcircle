import subprocess

from django.core.management import call_command
from django.core.management.base import NoArgsCommand


class Command(NoArgsCommand):
    """
    Wrapper to handle translation files:

    - Pull latest translations from transifex.
    - Write changes from transifex back to the db.
    - Create messages for django and extract strings from db.
    - Push translations to transifex.
    - If on branch develop: commit the changed files.

    """

    def handle_noargs(self, **options):
        # We need the current translations before creating new po files. Force
        # pull - this overwrites local changes!
        subprocess.call(['tx pull -f'], shell=True)

        # Update the configurations translations
        call_command('gettext_to_translation')

        # With everything fresh, create new po files.
        call_command('translation_to_gettext')

        # Create new po files for django translations
        call_command('makemessages')

        # Push to transifex.
        subprocess.call(['tx push -s -t'], shell=True)

        # Compile messages
        call_command('compilemessages')

        # Display command for a commit - if the current branch is 'develop'.
        branch = subprocess.check_output(
            "git rev-parse --abbrev-ref HEAD",
            stderr=subprocess.STDOUT,
            shell=True
        )
        if branch == 'develop':
            print('cd locale && '
                  'git add * && '
                  'git commit -m "Updated translations" && '
                  'cd -')

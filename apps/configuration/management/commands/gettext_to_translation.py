import collections
import contextlib
import re
from os.path import join

from django.conf import settings
from django.core.management.base import NoArgsCommand

from configuration.models import Translation


class Command(NoArgsCommand):
    """
    Write translated po-files back into the model, so it may be used with the
    configurations.

    """
    filename = 'extract'
    translations = collections.defaultdict()
    language_structure = {
        'model_info': [],
        'text': ''
    }

    def handle_noargs(self, **options):
        """
        Read translated files and write contents into the Translation model.

        """
        languages = dict(settings.LANGUAGES).keys()
        for language in languages:
            path = '{}/locale/{}/LC_MESSAGES/'.format(
                settings.BASE_DIR, language
            )
            with contextlib.suppress(FileNotFoundError):
                with open(join(path, '{}.po'.format(self.filename))) as f:
                    for line in self.get_translations(f.readlines()):
                        print(line)

    def get_translations(self, lines):
        """
        Args:
            lines: list of strings

        Returns:
            iterator: only lines that indicate model contents.

        """
        last_model_obj = None
        for line in lines:
            if re.match('# (\d+)', line):
                comment = line[2:].rstrip('\n').split('.')
                yield comment

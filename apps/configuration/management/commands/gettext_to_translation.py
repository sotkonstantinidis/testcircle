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
    translations = collections.defaultdict(dict)

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
                    self.get_translations(f.readlines())

        self.restore_to_orm()

    def get_translations(self, lines):
        """
        Parse the lines: extract information about models that is stored in the
        comments and the translated text. The result is written to
        self.translations.

        Args:
            lines: list of strings
        """
        pk = None
        bfr = []
        for line in lines:
            # For all lines that are a comment: extract information to a buffer.
            if re.match('# (\d+)', line):
                comment = line[2:].rstrip('\n').split('.')
                bfr.append(comment[1:])
                pk = comment[0]

            # If the msgstr is emtpy, take the value from the msgid.
            elif line.startswith('msgid') and pk:
                msgid = line

            # After comments, the actual text is found. Copy the text and buffer
            # to the global dict and empty the buffer.
            # When appending the buffer to the global dict, manage the structure
            # so that inserting into the orm is easy.
            elif line.startswith('msgstr') and pk:
                text = self.extract_text(line) or self.extract_text(msgid)
                for item in bfr:
                    # The innermost element must contain the text, all other
                    # keys are just dict keys wrapping the text.
                    pointer = self.translations[pk]
                    for key in item[:-1]:
                        pointer = pointer.setdefault(key, {})
                    pointer.update({item[-1]: text})
                pk = None
                bfr = []

    @staticmethod
    def extract_text(line):
        """
        Args:
            line: string

        Returns: extract translated content from string with msgid, msgstr.
        """
        return line[line.find('"')+1:line.rfind('"')]

    def restore_to_orm(self):
        """
        Write data from self.translations back into the model.

        """
        for pk, data in self.translations.items():
            translation = Translation.objects.get(pk=pk)
            translation.data = data
            translation.save()

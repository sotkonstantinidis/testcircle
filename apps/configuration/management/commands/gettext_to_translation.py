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
                    self.set_translations(f.readlines())

    def set_translations(self, lines):
        """
        Parse the lines: extract information about models that is stored in the
        comments and the translated text. The result is written to
        self.translations.

        Args:
            lines: list of strings
        """
        buffer = {}
        for line in lines:
            # For all lines that are a comment: extract information to a buffer.
            if re.match('# (\d+)', line):
                comment = line[2:].rstrip('\n').split('.')
                buffer.setdefault(comment[0], []).append(comment[1:])

            # If the msgstr is emtpy, take the value from the msgid.
            elif line.startswith('msgid') and buffer:
                msgid = line

            # After comments, the actual text is found.
            # Directly write the buffer to the model.
            elif line.startswith('msgstr') and buffer:
                text = self.extract_text(line) or self.extract_text(msgid)
                for pk, dict_keys in buffer.items():
                    for element in dict_keys:
                        self.create_dict_from_list(pk, element, text)
                # Reset the buffer after it was written to the orm.
                buffer = {}

    def create_dict_from_list(self, pk, keys, value):
        """
        Make a multidimensional array from the list (keys) and copy/overwrite
        the value to the model-instance.
        Not optimal regarding performance, but rather solid. And the feature
        was requested for yesterday.

        Args:
            pk: id
            keys: list
            value: string

        """
        obj = self.get_translation(pk)
        current_element = obj.data
        for key in keys[:-1]:
            current_element = current_element.setdefault(key, {})
        # The last element on the list is the language.
        current_element[keys[-1]] = value
        obj.save()

    @staticmethod
    def extract_text(line):
        """
        Args:
            line: string

        Returns: extract translated content from string with msgid, msgstr.
        """
        return line[line.find('"')+1:line.rfind('"')]

    def get_translation(self, pk):
        try:
            return Translation.objects.get(pk=pk)
        except Translation.DoesNotExist as e:
            # maybe: add logging here.
            raise e

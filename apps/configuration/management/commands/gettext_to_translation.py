# -*- coding: utf-8 -*-
import collections
import contextlib
import re
from os.path import join

from django.conf import settings

from configuration.models import Translation
from .base import DevelopNoArgsCommand


class Command(DevelopNoArgsCommand):
    """
    Write translated po-files back into the model, so it may be used with the
    configurations.

    """
    filename = 'extract'
    translations = collections.defaultdict(dict)
    lines = []

    def handle_noargs(self, **options):
        """
        Read translated files and write contents into the Translation model.
        """
        super(Command, self).handle_noargs(**options)
        languages = dict(settings.LANGUAGES).keys()

        for language in languages:
            path = '{}/locale/{}/LC_MESSAGES/'.format(
                settings.BASE_DIR, language
            )
            with contextlib.suppress(FileNotFoundError):
                with open(join(path, '{}.po'.format(self.filename))) as f:
                    self.lines = f.readlines()
                    self.set_translations()

    def set_translations(self):
        """
        Parse the lines: extract information about models that is stored in the
        comments and the translated text. The result is written to
        self.translations.

        Args:
            lines: list of strings
        """
        buffer = {}

        for index, line in enumerate(self.lines):
            # For all lines that are a comment: extract information to a buffer.
            if re.match('# (\d+)', line):
                comment = line[2:].rstrip('\n').split('.')
                buffer.setdefault(comment[0], []).append(comment[1:])

            # The content from 'msgid' is copied in case the 'msgstr' is empty.
            # This can be a multiline-string.
            elif line.startswith('msgid') and buffer:
                msgid = self.get_multiline_string(line, index)

            # After comments, the actual text is found. Directly write the
            # buffer to the model.
            elif line.startswith('msgstr') and buffer:
                text = self.get_multiline_string(line, index) or msgid
                for pk, dict_keys in buffer.items():
                    for element in dict_keys:
                        self.save_instance(pk, element, text)
                # Reset the buffer after it was written to the orm.
                buffer = {}

    def get_multiline_string(self, line, index):
        """
        A string can span multiple lines. Get all of them for the translation.

        Args:
            line: string Text of the current line
            index: int Current position in self.lines

        Returns:
            string: text of translation.

        """
        text = self.extract_text(line)
        index += 1
        while len(self.lines) > index and self.lines[index].startswith('"'):
            text += self.extract_text(self.lines[index])
            index += 1
        return text

    def save_instance(self, pk, keys, value):
        """
        Make a multidimensional array from the list (keys) and copy/overwrite
        the value to the model-instance.

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
        return line[line.find('"') + 1:line.rfind('"')]

    def get_translation(self, pk):
        try:
            return Translation.objects.get(pk=pk)
        except Translation.DoesNotExist as e:
            # maybe: add logging here.
            raise e

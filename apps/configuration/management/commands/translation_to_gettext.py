import collections
import contextlib
import re
import subprocess
from os.path import join
from django.conf import settings
from django.core.management.base import NoArgsCommand

from configuration.models import Translation


class Command(NoArgsCommand):
    """
    Extract all information about translations from the model into a
    po-file so the translators can work with that.

    After translating, the po-files can be imported with the command:
    gettext_to_translation
    """
    # intermediary file name.
    filename = 'extract'
    languages = collections.defaultdict(list)
    line = collections.namedtuple('Line', 'text comment')

    @property
    def settings_languages(self):
        return dict(settings.LANGUAGES).keys()

    def handle_noargs(self, **options):
        """
        Read all strints that must be translated from the json file, create a
        po-file from it that may be used in the default translation workflow.

        """
        # Get all strings that must be translated in a single dict, grouped by
        # language.
        self.make_language_dict()

        # Write a new file from the dict which then can be used with
        # pygettext to create pot-files and after that po-files.
        for language, lines in self.languages.items():
            path = '{}/locale/{}/LC_MESSAGES/'.format(
                settings.BASE_DIR, language
            )
            line_model_info = {}
            i = 2
            with open(join(path, '{}.py'.format(self.filename)), 'w+') as f:
                for line in lines:
                    f.write('{} \n'.format(line.comment))
                    f.write('_("{}") \n'.format(line.text))
                    line_model_info[i] = line.comment
                    i += 2

            # Create pot and then po file
            subprocess.call([self.get_pot_command(path)], shell=True)
            subprocess.call([self.get_po_command(path, language)], shell=True)

            # Replace comments with info about the model instance; this will be
            # used when inserting into the model after the translation.
            buffer = ''
            with open(join(path, 'extract.po'), 'r+') as po_file:
                for line in po_file.readlines():
                    if line.startswith('#: {}{}.py:'.format(path, self.filename)):
                        # Extract the number on the end of the line
                        index = re.findall('\d+', line[line.rfind(':')+1:])[0]
                        buffer += '{}\n'.format(line_model_info[int(index)])
                    else:
                        buffer += line

                # Erase file and write buffer into it.
                po_file.seek(0)
                po_file.truncate()
                po_file.write(buffer)

            # Remove unnecessary files.
            subprocess.call(['rm {}extract.pot'.format(path)], shell=True)
            subprocess.call(['rm {}{}.py'.format(path, self.filename)], shell=True)

    def make_language_dict(self):
        """
        Create a dict with all translation strings per language.
        """
        translations = Translation.objects.all()
        for translation in translations:
            for key, items in translation.data.items():
                self.walk(items, translation.id, key)

    def get_pot_command(self, path):
        return 'pygettext -d extract -p {path} {path}{filename}.py'.format(
                path=path, filename=self.filename)

    def get_po_command(self, path, lang):
        return 'msginit -i {path}{filename}.pot -o {path}{filename}.po ' \
               '--no-translator -l {lang}'.format(
                path=path, lang=lang, filename=self.filename)

    def walk(self, data, pk, path=''):
        """
        Recursively walk through the array.

        As the structure is not consistent, put only texts with a key that is a
        valid language onto the dict.

        Args:
            data: configuration.models.Translation
            pk: id
            path: string

        """
        for key, item in data.items():
            # Special case: keys for 'iso_3166' and such. Ignore them, they
            # don't need translation.
            if not isinstance(item, dict):
                return

            path += '.{}'.format(key)
            # If this is not the innermost element, continue
            if any([isinstance(value, dict) for value in item.values()]):
                path += '{}.'.format(key)
                self.walk(item, pk, path)
            else:
                # This is the innermost level of the dict.
                # Copy the value to the dict and make sure it's set for all
                # languages, even if it may not exist on the db.
                for lang in self.settings_languages:
                    comment = '# {}.{}.{}'.format(pk, path, lang)
                    self.languages[lang].append(
                        self.line(item.get(lang, item['en']), comment)
                    )

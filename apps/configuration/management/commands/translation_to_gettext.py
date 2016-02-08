import collections
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
    <tbd>
    """
    # intermediary file name.
    filename = 'extract'
    languages = collections.defaultdict(list)
    line = collections.namedtuple('Line', 'text comment')

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
        Create a dict with all translation strings per language. The language
        serves as key, all strings are in its dict. I.e.:
        'en': ['translateme', 'meetoo'],
        'es' ['foo']

        Returns: dict

        """
        translations = Translation.objects.all()
        for translation in translations:
            self.walk(translation.data, translation.id)

    def get_pot_command(self, path):
        return 'pygettext -d extract -p {path} {path}{filename}.py'.format(
                path=path, filename=self.filename)

    def get_po_command(self, path, lang):
        return 'msginit -i {path}{filename}.pot -o {path}{filename}.po ' \
               '--no-translator -l {lang}'.format(
                path=path, lang=lang, filename=self.filename)

    def walk(self, translation, pk, path=''):
        """
        Recursively walk through the array.

        As the structure is not consistent, put only texts with a key that is a
        valid language onto the dict.

        Args:
            translation: configuration.models.Translation
            pk: id
            path: string

        """
        for key, item in translation.items():
            if isinstance(item, dict):
                path += '{}.'.format(key)
                self.walk(item, pk, path)
            else:
                if key in dict(settings.LANGUAGES).keys():
                    comment = '# {}.{}{}'.format(pk, path, key)
                    self.languages[key].append(self.line(item, comment))

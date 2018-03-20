from .base import Edition


class Technologies(Edition):
    """
    Questionnaire updates for carbon benefit.
    """
    type = 'technologies'

    def country_as_checkbox(self):
        return {
            'diff': '',
            'help_text': 'Unstructured text is now a list of given options'
        }


def run_migration(apps, schema_editor):
    """
    Use this in your migration file, create an empty migration with:

    python manage.py makemigrations configuration --empty

    And add this tho the operations:

    operations = [
        migrations.RunPython(run_migration)
    ]

    """
    Configuration = apps.get_model("configuration", "Configuration")
    Technologies().run_operations(configuration=Configuration)

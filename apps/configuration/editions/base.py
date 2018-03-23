from ..configuration import QuestionnaireConfiguration
from ..models import Configuration


class Edition:
    """
    Base class for a new edition of a questionnaire configuration.

    Provides a central interface for:
    - callable to migrate data (run_migration); forwards migrations only!
    - helpers for changes in the configuration ('diff')
    - some global utilities (help texts and such).

    """

    type = ''
    edition = ''
    operations = []

    def __init__(self):
        """
        Load operations, and validate the required instance variables.
        """
        self._set_operations()

        for required_variable in ['type', 'edition', 'operations']:
            if not getattr(self, required_variable):
                raise NotImplementedError('Instance variable "%s" is required' % required_variable)

    def _set_operations(self):
        """
        Collect all methods decorated with @callable and append them to the operations-list.
        """
        for method_name in filter(lambda name: not name.startswith('__'), dir(self)):
            method = getattr(self, method_name)
            if hasattr(method, 'is_operation') and getattr(method, 'is_operation'):
                self.operations.append(method)

    def run_operations(self, configuration: Configuration):
        """
        - Collect 'previous' configuration,
        - Apply operations, as defined by self.operations[]
        - save it (if valid)

        """
        data = Configuration.latest_by_type(type=self.type).data

        for operation in self.operations:

            # as of now, 'diff' is a callable.
            # how is it executed?
            # where is the help-text needed?
            # the current solution is nasty - this needs discussion!
            data = operation()['diff'](data)

        # Check: Must a configuration be saved before it can be loaded / validated?
        obj = self.save_object(configuration=configuration, data=data)

        QuestionnaireConfiguration(keyword=obj.type)

    def save_object(self, configuration: Configuration, data: dict):
        obj = configuration(
            edition=self.edition,
            type=self.type,
            data=data
        )
        obj.save()
        return obj

    def get_help_text(self):
        pass

    @classmethod
    def run_migration(cls, apps, schema_editor):
        """
        Callable for your migration file. Create an empty migration with:

        ```python manage.py makemigrations configuration --empty```

        Add this tho the operations list:

        operations = [
            migrations.RunPython(run_migration)
        ]

        """
        Configuration = apps.get_model("configuration", "Configuration")
        cls().run_operations(configuration=Configuration)


def operation(func):
    """
    Set an attribute to the wrapped method, so it is appended to the list of operations.
    """
    func.is_operation = True
    return func

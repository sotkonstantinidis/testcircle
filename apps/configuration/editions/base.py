from django.template.loader import render_to_string

from configuration.models import Configuration, Key, Value, Translation


class Edition:
    """
    Base class for a new edition of a questionnaire configuration, providing a central interface for:

    - Simple, explicit definition for changes in configuration
      - Re-use of operations, with possibility of customizing them (callables)
      - Changes can be tracked per question between editions

    - Verbose display of changes before application

    - Generic helper methods for help texts, release notes and such

    """

    code = ''
    edition = ''

    def __init__(self, key: Key, value: Value, configuration: Configuration, translation: Translation):
        """
        Load operations, and validate the required instance variables.

        """
        self.key = key
        self.value = value
        self.configuration = configuration
        self.translation = translation
        self.operations = []
        self._set_operation_methods()
        self.validate_instance_variables()

    def validate_instance_variables(self):
        for required_variable in ['code', 'edition', 'operations']:
            if not getattr(self, required_variable):
                raise NotImplementedError('Instance variable "%s" is required' % required_variable)

        if self.code not in [code[0] for code in Configuration.CODE_CHOICES]:
            raise AttributeError('Code %s is not a valid configuration code choice' % self.code)

    def _set_operation_methods(self):
        """
        Collect all properties that provide an Operation.

        """
        for method_name in filter(lambda name: not name.startswith('__'), dir(self)):
            method = getattr(self, method_name)
            if isinstance(method, Operation):
                self.operations.append(method)

    def run_operations(self):
        """
        Apply operations, as defined by self.operations

        """
        data = self.configuration.objects.filter(
            code=self.code
        ).exclude(
            code=self.code, edition=self.edition
        ).latest('created').data
        for _operation in self.operations:
            data = _operation.migrate(**data)

        self.save_object(**data)

    def save_object(self, **data) -> Configuration:
        """
        Create or update the configuration with the modified data.

        """
        obj, _ = self.configuration.objects.get_or_create(
            edition=self.edition,
            code=self.code
        )
        obj.data = data

        # @TODO: validate data before calling save
        obj.save()
        return obj

    def get_release_notes(self):
        for _operation in self.operations:
            _operation.render()

    @classmethod
    def run_migration(cls, apps, schema_editor):
        """
        Callable for the django migration file. Create an empty migration with:

        ```python manage.py makemigrations configuration --empty```

        Add this tho the operations list:

        operations = [
            migrations.RunPython(<Subclass>.run_migration)
        ]

        """
        Configuration = apps.get_model("configuration", "Configuration")
        Key = apps.get_model("configuration", "Key")
        Value = apps.get_model("configuration", "Value")
        Translation = apps.get_model("configuration", "Translation")
        cls(key=Key, value=Value, configuration=Configuration, translation=Translation).run_operations()


class Operation:
    """
    Data structure for an 'operation' method.
    Centralized wrapper for all operations, so they can be extended / modified in a single class.

    """
    default_template = ''

    def __init__(self, transformation: callable, release_note: str, **kwargs):
        self.transformation = transformation
        self.release_note = release_note
        self.template_name = kwargs.get('template_name', self.default_template)

    def migrate(self, **data) -> dict:
        return self.transformation(**data)

    def render(self) -> str:
        return render_to_string(
            template_name=self.template_name,
            context={'note': self.release_note}
        )

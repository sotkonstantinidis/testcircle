from configuration.models import Configuration


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
    operations = []

    def __init__(self):
        """
        Load operations, and validate the required instance variables.

        """
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
        Collect all methods decorated with @operation and append them to the operations-list.

        """
        for method_name in filter(lambda name: not name.startswith('__'), dir(self)):
            method = getattr(self, method_name)
            if hasattr(method, 'is_operation') and getattr(method, 'is_operation'):
                #_operation = method()
                #if not isinstance(_operation, Operation):
                #    raise ValueError('Only subclasses of "Operation" are allowed')
                self.operations.append(method)

    def run_operations(self, configuration: Configuration):
        """
        Apply operations, as defined by self.operations

        """
        data = configuration.latest_by_code(code=self.code).data
        for _operation in self.operations:
            # data = _operation.migrate(**data)
            data = _operation(**data)

        self.save_object(configuration=configuration, **data)

    def save_object(self, configuration: Configuration, **data) -> Configuration:
        """
        Create or update the configuration with the modified data.

        """
        obj, _ = configuration.objects.get_or_create(
            edition=self.edition,
            code=self.code
        )
        obj.data = data

        # @TODO: validate data before calling save
        obj.save()
        return obj

    def get_help_text(self):
        pass

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
        cls().run_operations(configuration=Configuration)


class Operation:
    """
    Data structure for an 'operation' method.
    Centralized wrapper for all operations, so they can be extended / modified in a single class.

    As of now, simply apply the transformation to given data.
    At a later point, this should also include the 'keywords' of changed questions, so the context
    aware help can be built easily.

    @todo: discuss - is this over-engineering or necessary for future development? right now,
    this is not in use...

    """
    def __init__(self, transformation: callable):
        self.transformation = transformation

    def migrate(self, **data) -> dict:
        return self.transformation(**data)


def operation(func):
    """
    Set an attribute to the wrapped method, so it is appended to the list of operations.

    """
    func.is_operation = True
    return func

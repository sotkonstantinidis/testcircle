from ..models import Configuration


class Edition:
    """
    Base class for a new edition.
    Provides helpers for changes in the configuration ('diff') and some global utilities (help
    texts and such).
    """

    type = ''
    operations = []

    def __init__(self):
        if not self.type:
            raise NotImplementedError('Type is required')

    def run_operations(self, configuration: Configuration):
        """
        Load previous
        Apply operations
        Validate
        Save
        """
        pass

    def helper_fn(self):
        pass

    def get_help_text(self):
        pass



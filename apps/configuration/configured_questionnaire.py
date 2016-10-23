import collections
import functools

from .configuration import QuestionnaireConfiguration


class ConfiguredQuestionnaire:
    """
    Combine given configuration and data into a single ordered dict.
    """
    nodes = [
        'sections',
        'categories',
        'subcategories',
        'questiongroups',
        'questions'
    ]
    store = collections.OrderedDict()
    tmp_path = []  # all dict keys until the current element
    tmp_values = {}  # store question-values for current questiongroup

    def __init__(self, config, **data):
        self.values = data
        self.values_keys = self.values.keys()
        self.get_children(config)

    def get_children(self, config: QuestionnaireConfiguration, index=0):
        """
        Walk through the configuration and build a 'store' with all nested
        elements, adding the filled in values from self.data.
        """
        children = getattr(config, self.nodes[index])
        is_question = index >= len(self.nodes) - 1

        for child in children:
            # Reset the path for root elements.
            if index == 1:
                self.tmp_path = []

            # Append current values to the store
            self.active_child_in_store[child.keyword] = {
                'label': str(child.label),
                'children': {}
            }
            # Temporary helpers; the filled in questions are grouped by its
            # questiongroup.
            if self.nodes[index] == 'questiongroups':
                self.tmp_values = {}
                if child.keyword in self.values_keys:
                    # todo: discuss with lukas: if multiple list items are
                    # available, what does this mean? the questiongroup consists
                    # of the same question only?
                    self.tmp_values = self.values[child.keyword][0]

            # Add the 'path' to the current element, so the next iteraction can
            # access this element and append to it.
            self.tmp_path.extend([child.keyword, 'children'])

            # If the current element is not a question, iterate 'down' into the
            # next level of the config.
            if not is_question:
                self.get_children(child, index + 1)
            else:
                self.put_question_data(child)

    def put_question_data(self, child):
        self.active_child_in_store[child.keyword] = {
            'label': str(child.label),
            'value': self.tmp_values.get(child.keyword) or ''
        }

    @property
    def active_child_in_store(self):
        return functools.reduce(dict.get, self.tmp_path, self.store)


class ConfiguredQuestionnaireSummary(ConfiguredQuestionnaire):
    """
    Get only data which is configured to appear in the summary.
    """
    data = []

    def put_question_data(self, child):
        if hasattr(child, 'is_in_summary') and child.is_in_summary:
            self.data.append({
                'keyword': child.keyword,
                'label': str(child.label),
                'value': self.tmp_values.get(child.keyword) or ''
            })

import collections
import functools

from .configuration import QuestionnaireQuestion


class ConfiguredQuestionnaire:
    """
    Combine given configuration and data into a single ordered dict.
    """
    store = collections.OrderedDict()
    tmp_path = []  # all dict keys until the current element

    def __init__(self, config, **data):
        self.values = data
        self.values_keys = self.values.keys()
        self.get_children(config)

    def get_children(self, config):
        """
        Walk through the configuration and build a 'store' with all nested and
        sibling elements, adding the filled in values from self.data.
        """
        children = getattr(config, 'children')

        for child in children:
            # Append current values to the store
            self.active_child_in_store[child.keyword] = {
                'label': str(child.label),
                'children': {}
            }

            # If the current element is not a question, iterate 'down' into the
            # next level of the config.
            if isinstance(child, QuestionnaireQuestion):
                self.put_question_data(child)
            else:
                # Add the 'path' to the current element, so the next iteration
                # can access this element and append to it.
                self.tmp_path.extend([child.keyword, 'children'])
                self.get_children(child)

        # Go back to the parent element.
        self.tmp_path = self.tmp_path[:-2]

    def put_question_data(self, child):
        value = self.values.get(child.parent_object.keyword)
        self.active_child_in_store[child.keyword] = {
            'label': str(child.label),
            'value': child.get_details(value[0]) if value else ''
        }

    @property
    def active_child_in_store(self):
        return functools.reduce(dict.get, self.tmp_path, self.store)


class ConfiguredQuestionnaireSummary(ConfiguredQuestionnaire):
    """
    Get only data which is configured to appear in the summary.
    """
    data = {}

    def put_question_data(self, child: QuestionnaireQuestion):
        # add named 'part' in configuration
        if hasattr(child, 'is_in_summary') and child.is_in_summary:
            self.data.update({
                '{}.{}'.format(child.questiongroup.keyword, child.keyword): {
                    'keyword': child.keyword,
                    'label': str(child.label),
                    'value': self.tmp_values.get(child.keyword) or ''
                }
            })

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
            # Build nested elements while iterating through them.
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

    def put_question_data(self, child: QuestionnaireQuestion):
        """
        Store the child's data, including the value.
        """
        self.active_child_in_store[child.keyword] = {
            'label': str(child.label),
            'value': self.get_value(child)
        }

    def get_value(self, child):
        """
        Get the template values as defined in the QuestionnaireQuestion config.
        """
        child.view_options['template'] = 'raw'
        value = self.values.get(child.parent_object.keyword)
        # Value may be empty, a list of one element (most of the time) or a list
        # of dicts for nested questions.
        if not value:
            return ''
        elif len(value) == 1:
            return child.get_details(data=value[0])
        else:
            return [child.get_details(single_value) for single_value in value]

    @property
    def active_child_in_store(self):
        return functools.reduce(dict.get, self.tmp_path, self.store)


class ConfiguredQuestionnaireSummary(ConfiguredQuestionnaire):
    """
    Get only data which is configured to appear in the summary. This is defined
    by the configuration-field: 'in_summary', which specifies the section
    of the summary for given field for the chosen summary-config (e.g. 'full',
    'one page', 'four page').
    """
    data = []

    def __init__(self, summary_type, *args, **kwargs):
        self.summary_type = summary_type
        super().__init__(*args, **kwargs)

    def put_question_data(self, child: QuestionnaireQuestion):
        if child.in_summary and child.in_summary.get(self.summary_type):
            self.data.append({
                '{}.{}'.format(child.questiongroup.keyword, child.keyword): {
                    'keyword': child.keyword,
                    'label': str(child.label),
                    'value': self.get_value(child)
                }
            })

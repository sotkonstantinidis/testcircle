import collections
import functools
import logging
from copy import copy

from django.conf import settings
from .configuration import QuestionnaireQuestion

logger = logging.getLogger(__name__)


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
        # Copy the original value, so it can be re-applied. This is important
        # so the other instances of this config get the expected value.
        original_template_value = child.view_options.get('template', {})
        child.view_options['template'] = 'raw'
        value = self.values.get(child.parent_object.keyword)
        # Value may be empty, a list of one element (most of the time) or a list
        # of dicts for nested questions.
        if not value:
            val =  ''
        elif len(value) == 1:
            val = child.get_details(data=value[0])
        else:
            # If 'copy' is omitted, the same instance is returned for all values
            # I don't see why - but at this point, this seems the only
            # workaround.
            val = [copy(child.get_details(single_value)) for single_value in value]

        child.view_options['template'] = original_template_value
        return val

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
    data = {}

    def __init__(self, summary_type, *args, **kwargs):
        self.summary_type = summary_type
        super().__init__(*args, **kwargs)

    def put_question_data(self, child: QuestionnaireQuestion):
        """
        Put the value to self.data, using the name as defined in the config
        ('in_summary': {'this_type': <key_name>}}.
        As some key names are duplicated by virtue (config may use the same
        question twice), but represent different and important content, some
        keys are overridden with the help of the questions questiongroup.

        This cannot be solved on the config as the same question is listed
        twice, so the key-name overriding setting must be ready for versioning.

        """
        if child.in_summary and child.in_summary.get(self.summary_type):
            field_name = child.in_summary[self.summary_type]
            field_with_qg = '{questiongroup}.{field}'.format(
                questiongroup=child.questiongroup.keyword,
                field=field_name
            )
            overridden_key = settings.CONFIGURATION_SUMMARY_KEY_OVERRIDE.get(
                field_with_qg, field_name
            )
            if overridden_key not in self.data:
                self.data[overridden_key] = self.get_value(child)
            else:
                # This can be intentional, e.g. header_image is a list. In this
                # case, only the first element is available.
                logger.warn(
                    'The field {key} for the summary {summary_type} is defined '
                    'more than once'.format(
                        key=child.in_summary[self.summary_type],
                        summary_type=self.summary_type
                    )
                )

import collections
import functools
import json
import logging
from copy import copy

from django.conf import settings
from questionnaire.models import Questionnaire
from questionnaire.templatetags.questionnaire_tags import get_static_map_url

from .configuration import QuestionnaireQuestion

logger = logging.getLogger(__name__)


class ConfiguredQuestionnaire:
    """
    Combine given configuration and data into a single ordered dict.
    """
    store = collections.OrderedDict()
    tmp_path = []  # all dict keys until the current element

    def __init__(self, config, questionnaire, **data):
        self.values = data
        self.questionnaire = questionnaire
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

    def get_value(self, child: QuestionnaireQuestion):
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
            val = child.get_details(
                data=value[0], questionnaire_object=self.questionnaire
            )
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

    def __init__(self, config, summary_type: str, questionnaire: Questionnaire, **data):
        self.summary_type = summary_type
        super().__init__(questionnaire=questionnaire, config=config, **data)

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
            qg_field = '{questiongroup}.{field}'.format(
                questiongroup=child.questiongroup.keyword,
                field=field_name
            )
            override = settings.CONFIGURATION_SUMMARY_OVERRIDE.get(qg_field, {})
            field_name = override.get('override_key', field_name)
            get_value_fn = override.get(
                'override_fn', lambda self, child: self.get_value(child)
            )

            if field_name not in self.data:
                self.data[field_name] = get_value_fn(self, child)
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

    def extract_coordinates(self, features):
        """
        Get only Points, and the first set of coordinates for them.
        """
        for point in features:
            if point['geometry']['type'] == 'Point':
                yield ', '.join(map(str, point['geometry']['coordinates']))

    def get_map_values(self, child: QuestionnaireQuestion):
        """
        Configured function (see ConfigurationConf) for special preparation of
        data to display map data.
        """
        value = self.get_value(child).get('value', {})
        features = json.loads(value).get('features', [])
        # todo: ask lukas: is there a nicer option?
        return {
            'img_url': get_static_map_url(self.questionnaire),
            'coordinates': self.extract_coordinates(features)
        }

    def get_full_range_values(self, child: QuestionnaireQuestion):
        values = self.values.get(child.parent_object.keyword)
        if len(values) != 1:
            raise NotImplementedError()
        selected = values[0].get(child.keyword)
        for choice in child.choices:
            yield {'highlighted': choice[0] in selected, 'text': choice[1]}

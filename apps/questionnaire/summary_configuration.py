import logging

from django.conf import settings
from configuration.configuration import QuestionnaireQuestion
from configuration.configured_questionnaire import ConfiguredQuestionnaire
from .models import Questionnaire
from .templatetags.questionnaire_tags import get_static_map_url

logger = logging.getLogger(__name__)


class ConfiguredQuestionnaireSummary(ConfiguredQuestionnaire):
    """
    Get only data which is configured to appear in the summary. This is defined
    by the configuration-field: 'in_summary', which specifies the section
    of the summary for given field for the chosen summary-config (e.g. 'full',
    'one page', 'four page').
    """

    def __init__(self, config, summary_type: str,
                 questionnaire: Questionnaire, **data):
        self.summary_type = summary_type
        self.data = {}
        self.config_object = config
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
                logger.warning(
                    'The field {key} for the summary {summary_type} is defined '
                    'more than once'.format(
                        key=child.in_summary[self.summary_type],
                        summary_type=self.summary_type
                    )
                )

    def get_map_values(self, child: QuestionnaireQuestion):
        """
        Configured function (see ConfigurationConf) for special preparation of
        data to display map data.
        """
        if not self.questionnaire.geom:
            return {'img_url': '', 'coordinates': ''}
        else:
            return {
                'img_url': get_static_map_url(self.questionnaire),
                'coordinates': self.questionnaire.geom.coords
            }

    def get_full_range_values(self, child: QuestionnaireQuestion):
        """
        Get all available elements, with the selected ones highlighted.
        """
        values = self.values.get(child.parent_object.keyword)
        # elements without a selected value must be shown, if more than one list
        # of values exists, this method must be extended.
        if values and len(values) == 1:
            selected = values[0].get(child.keyword)
        else:
            logger.warning(msg='No or more than one list of values is set '
                               'for %s' % child.keyword)
            selected = []
        for choice in child.choices:
            yield {'highlighted': choice[0] in selected, 'text': choice[1]}

    def get_picto_and_nested_values(self, child: QuestionnaireQuestion):
        """
        Get selected element with parents and pictos. The given question may
        be a child of several nested questiongroups.
        """
        try:
            selected = self.get_value(child)[0]['values']
        except (KeyError, IndexError):
            return None

        # get all nested elements in the form '==question|nested'...
        nested_elements_config = child.form_options.get('questiongroup_conditions')
        # ..and split the strings to a more usable dict.
        nested_elements = dict(self.split_raw_children(*nested_elements_config))
        choices = dict(child.choices)

        for value in selected:
            child_text = []
            # 'value' is a tuple of four elements: title, icon-url, ?, keyword
            # this represents the 'parent' question with an image
            selected_children_keyword = nested_elements.get(value[3])
            # selected_children are the 'sub-selections' of given 'value'
            if selected_children_keyword:
                # load the configured question for the children and get their
                # labels - they will be concatenated as 'text' below.
                # the structure is nested as follows:
                # [{'keyword': 'value'}, {'keyword', 'value'}]
                for selected_child in self.values.get(selected_children_keyword, {}):
                    for child_keyword, child_value in selected_child.items():
                        if isinstance(child_value, list):
                            # [c.keyword for c in self.config_object.get_questiongroup_by_keyword(selected_children_keyword).children]
                            # todo: continue here.
                            pass
                        configured_child = self.config_object.get_question_by_keyword(
                            questiongroup_keyword=selected_children_keyword,
                            keyword=child_keyword
                        )
                        child_text.append('{label}: {value}'.format(
                            label=configured_child.label,
                            value=child_value
                        ))

            yield {
                'url': value[1],
                'label': value[0],
                'text': '{title}: {child_text}'.format(
                    title=choices.get(value[3]),
                    child_text=', '.join(child_text)
                ),
            }

    def split_raw_children(self, *children):
        """
        Split the list of raw strings and strip the unnecessary chars
        """
        for child in children:
            lhs, rhs = child.split('|')
            yield self.stripchars(lhs), self.stripchars(rhs)

    @staticmethod
    def stripchars(raw: str) -> str:
        strip = ['=', "'"]
        return ''.join([c for c in raw if c not in strip])

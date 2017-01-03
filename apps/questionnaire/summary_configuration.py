import logging
import itertools
import operator

from configuration.configuration import QuestionnaireQuestion, \
    QuestionnaireSubcategory
from configuration.configured_questionnaire import ConfiguredQuestionnaire
from qcat.errors import ConfigurationError
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
        if child.in_summary and self.summary_type in child.in_summary['types']:
            options = {
                **child.in_summary['default'],
                **child.in_summary.get(self.summary_type, {})
            }
            if 'field_name' not in options:
                raise ConfigurationError(
                    'At least a unique field name must be set for "in_summary" '
                    'config for the question {}.'.format(child.keyword)
                )
            field_name = self.get_configured_field_name(
                child=child,
                field_name=options['field_name']
            )

            if field_name not in self.data:
                self.data[field_name] = self.get_configured_value(
                    child=child, **options
                )
            else:
                # This can be intentional, e.g. header_image is a list. In this
                # case, only the first element is available.
                logger.warning(
                    'The field {field_name} for the summary {summary_type} '
                    'is defined more than once'.format(
                        field_name=field_name,
                        summary_type=self.summary_type
                    )
                )

    def get_configured_value(self, child: QuestionnaireQuestion, **kwargs):
        configured_fn = kwargs.get('get_value')
        if not configured_fn:
            return self.get_value(child=child)
        else:
            fn = getattr(self, configured_fn['name'])
            return fn(child=child, **configured_fn.get('kwargs', {}))

    def get_configured_field_name(self, child: QuestionnaireQuestion,
                                  field_name: str) -> str:
        if not isinstance(field_name, dict):
            return field_name
        else:
            qg_field = '{questiongroup}.{field}'.format(
                questiongroup=child.questiongroup.keyword,
                field=child.keyword
            )
            try:
                return field_name[qg_field]
            except KeyError:
                raise ConfigurationError('No field_name for '
                                         'summary field {}'.format(qg_field))

    def get_map_values(self, child: QuestionnaireQuestion) -> dict:
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

    def get_full_range_values(self, child: QuestionnaireQuestion,
                              is_radio=False):
        """
        Get all available elements, with the selected ones highlighted.
        """
        values = self.values.get(child.parent_object.keyword)
        # elements without a selected value must be shown, if more than one list
        # of values exists, this method must be extended.
        if values and len(values) == 1:
            selected = values[0].get(child.keyword, [])
        else:
            logger.warning(msg='No or more than one list of values is set '
                               'for %s' % child.keyword)
            selected = []

        # default is 'checkbox', where multiple elements can be selected.
        is_highlighted = operator.eq if is_radio else operator.contains

        for choice in child.choices:
            yield {
                'highlighted': is_highlighted(selected, choice[0]),
                'text': choice[1]
            }

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
        nested_elements_config = child.form_options.get(
            'questiongroup_conditions')
        # ..and split the strings to a more usable dict.
        nested_elements = dict(self.split_raw_children(*nested_elements_config))

        for value in selected:
            child_text = ''
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
                        # The child element is part of a questiongroup.
                        child_question = self.config_object.get_question_by_keyword(
                            questiongroup_keyword=selected_children_keyword,
                            keyword=child_keyword
                        )
                        child_text += self._concatenate_child_question_texts(
                            child_question=child_question,
                            selected_child_len=len(selected_child.keys()),
                            values=child_value
                        )
            yield {
                'url': value[1],
                'title': value[0],
                'text': child_text
            }

    def get_qg_values_with_scale(self, child):
        try:
            values = self.values.get(child.parent_object.keyword, [])[0]
        except IndexError:
            values = {}

        for child in child.questiongroup.children:
            yield {
                'label': child.label,
                'range': len(child.choices),
                'min': child.choices[0][1],
                'max': child.choices[-1][1],
                'selected': values.get(child.keyword, '')
            }

    def _concatenate_child_question_texts(
            self, child_question: QuestionnaireQuestion,
            selected_child_len: int, values: list) -> str:
        """
        Helper to print nice concatenated strings
        """
        choices_labels = dict(child_question.choices)
        # Show label only if it is configured to be shown
        has_label = child_question.view_options.get('label_position') != 'none'
        # If more than one element is selected for the current
        # group, add a newline
        text_parts = dict(
            label='{}: '.format(child_question.label) if has_label else '',
            multi_line='<br>' if selected_child_len > 1 else '',
            text=', '.join([choices_labels[choice] for choice in values]),
        )
        return '{label}{text}{multi_line}'.format_map(text_parts)

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

    def get_table(self, child: QuestionnaireQuestion):
        """
        needs discussion - is the output format really correct?
        """
        questiongroups = self.get_questiongroups_in_table(
            section=child.questiongroup.parent_object
        )
        table = []
        for questiongroup in questiongroups:
            items = []
            for question in questiongroup.questions:
                values = self.get_value(child=question)
                items.append({
                    '0': '',
                    '1': '',
                    '2': ''
                })
            table.append({
                'head': questiongroup.label,
                'items': items
            })
        return table

    def get_questiongroups_in_table(self, section: QuestionnaireSubcategory):
        """
        Get only questiongroups that are configured to be shown in the table.
        """
        used = list(itertools.chain(*section.table_grouping))
        for questiongroup in section.questiongroups:
            if questiongroup.keyword in used:
                yield questiongroup

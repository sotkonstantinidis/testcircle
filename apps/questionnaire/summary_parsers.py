"""
Parse data of combined configuration and questionnaire-data and provide some
additional methods to extract data as required for the summary.
"""

import collections
import contextlib
import itertools
import logging
import operator

from configuration.configuration import QuestionnaireQuestion, \
    QuestionnaireSubcategory, QuestionnaireQuestiongroup
from configuration.configured_questionnaire import ConfiguredQuestionnaire
from qcat.errors import ConfigurationError
from .models import Questionnaire
from .templatetags.questionnaire_tags import get_static_map_url

logger = logging.getLogger(__name__)


class ConfiguredQuestionnaireParser(ConfiguredQuestionnaire):
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

    def get_qg_values_with_scale(self, child: QuestionnaireQuestion, **kwargs):
        """
        The same output format (see _qg_scale_format) is expected for various
        question formats/styles. Maybe: move to separate functions.
        """
        if kwargs.get('qg_style') == 'multi_select':
            # e.g. 6.1. - list only selected options. Get all questions from
            # the parent Category and append comments.
            categories = child.questiongroup.parent_object.parent_object.subcategories
            questiongroups = itertools.chain(
                *[category.questiongroups for category in categories]
            )
            for group in questiongroups:
                value = self._get_qg_selected_value(group.children[0])
                # Omit empty questions or 'other' questions.
                if not value or not isinstance(value, int):
                    continue

                kwargs = group.children[0].additional_translations
                if len(group.children) > 2:
                    comment = self._get_qg_selected_value(group.children[3])
                    kwargs['comment'] = comment or ''

                yield from self._qg_scale_format(
                    child=group.children[0],
                    value=value,
                    **kwargs
                )

        if kwargs.get('qg_style') == 'click_labels':
            # e.g. 5.9 - get all info from parent questiongroup
            for child in child.questiongroup.children:
                yield from self._qg_scale_format(
                    child=child,
                    value=self._get_qg_selected_value(child),
                    label_left=child.choices[0][1],
                    label_right=child.choices[-1][1]
                )

        if kwargs.get('qg_style') == 'radio':
            # e.g. 6.4. - all info from radio buttons
            values = self._get_qg_selected_value(child, all_values=True)

            for child in child.questiongroup.children:
                str_value = values.get(child.keyword, '')
                # in the template, the numeric position of the value in the
                # 'range' is required.
                with contextlib.suppress(ValueError):
                    choice_keys = dict(child.choices).keys()
                    value = list(choice_keys).index(str_value) + 1

                yield from self._qg_scale_format(
                    child=child,
                    value=value,
                    label_left=child.choices[0][1],
                    label_right=child.choices[-1][1]
                )

    def _get_qg_selected_value(self, child: QuestionnaireQuestion,
                               all_values=False):
        values = {}
        with contextlib.suppress(IndexError):
            values = self.values.get(child.questiongroup.keyword, [])[0]
        return values.get(child.keyword) if not all_values else values

    def _qg_scale_format(self, child: QuestionnaireQuestion, value: int,
                         **kwargs):
        yield {
            'label': kwargs.get('label', child.label),
            'range': range(0, kwargs.get('range', len(child.choices))),
            'min': kwargs.get('label_left'),
            'max': kwargs.get('label_right'),
            'selected': value - 1 if value else None,
            'comment': kwargs.get('comment', '')
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
        Feedback was requested, but no answer given. This output format is
        assumed to be fine.
        """
        table = {
            'head': collections.defaultdict(dict),
            'partials': []
        }
        questiongroups = self.get_questiongroups_in_table(
            section=child.questiongroup.parent_object
        )
        # structure:
        # a questiongroup consists of typically 6 questions. these are the
        # columns. the number of columns is fixed for all questiongroups in
        # the table.
        # the rows are the values that the user has filled in (0-n).
        # so always print the 'header' row, and 0-n rows with values
        for questiongroup in questiongroups:
            partials = collections.OrderedDict()

            for column, question in enumerate(questiongroup.questions):
                column = str(column)
                values = self.get_value(child=question)

                # Special case: the total is saved in the last question. Skip
                # creating the table header and such, and only fill in the
                # minimal necessary values.
                if question.keyword.endswith('_total_costs'):
                    table['total'] = {
                        'label': values[0].get('key'),
                        'value': values[0].get('value'),
                    }
                    continue

                for row, value in enumerate(values):
                    if not table['head'][column] and value.get('key'):
                        table['head'][column] = value['key']
                    element = partials.setdefault(row, {})
                    element[column] = value.get('value') or ''

            if partials:
                table['partials'].append({
                    'head': questiongroup.label,
                    'items': partials.values()
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


class TechnologyParser(ConfiguredQuestionnaireParser):

    def get_climate_change(self, child: QuestionnaireQuestion):
        # based on this first question, get all questiongroups with at least
        # one # filled in question.
        climate_change_categories = child.questiongroup.parent_object.\
            parent_object.parent_object
        groups = []

        for main_category in filter(self._subcategory_has_value,
                                    climate_change_categories.subcategories):

            # A store for all 'lines' for the main groups
            items = []
            questiongroups = [subcategory.questiongroups for subcategory in
                              main_category.subcategories]
            for group in itertools.chain(*questiongroups):

                values = self.values.get(group.keyword, [])
                # if more than one element is available, a set of 'sibling'
                # questions was filled in. Duplicate this question, resulting
                # in one line per value/answer.
                for value in values:
                    items.append(self._prepare_climate_change_row(group, **value))

            groups.append({
                'title': main_category.label,
                'items': items
            })

        return groups

    def _prepare_climate_change_row(self, group: QuestionnaireQuestiongroup, **values):
        """
        Create elements for a single line
        """
        label = group.label
        comment = ''

        # One set of questions equals one line in the summary. The field names
        # are stable/repeating so string comparison is nasty but semi-ok.
        for question in group.questions:

            if question.keyword == 'tech_exposure_incrdecr':
                # Indicator for direction of development (increased/decreased)
                question_label = values.get(question.keyword)
                if question_label:
                    label += ' {}'.format(question_label)

            elif question.keyword == 'tech_exposure_sensitivity':
                # The actual value for our range-field.
                # The first and the last choice are irrelevant to this
                # mode of layout. If the selected value is empty or unknown,
                # this is added as comment.
                choice_keys = list(
                    dict(question.choices).keys() - ['', 'cope_unknown']
                )

                value = values.get(question.keyword)
                if value not in choice_keys:
                    string_value = dict(question.choices).get(value)
                    comment += ' Answer: {}'.format(string_value)
                else:
                    value = choice_keys.index(value) + 1

            else:
                # All other fields, such as 'season' go into the comments.
                comment_key = values.get(question.keyword)
                if comment_key:
                    comment += '{label}: {value}'.format(
                        label=question.label,
                        value=dict(question.choices).get(comment_key)
                    )
        return {
            'label': label,
            'range': range(0, len(choice_keys)),
            'min': question.choices[1][1],
            'max': question.choices[-2][1],
            'selected': value,
            'comment': comment
        }

    def _subcategory_has_value(self, subcategory):
        """
        Filter only questiongroups with at least one filled in question.
        """
        questiongroups = itertools.chain(
            *[subcategory.questiongroups for subcategory in subcategory.subcategories]
        )
        qg_keywords = [qg.keyword for qg in questiongroups]
        return not set(qg_keywords).isdisjoint(set(self.values.keys()))

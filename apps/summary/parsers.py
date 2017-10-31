"""
Parse data of combined configuration and questionnaire-data and provide some
additional methods to extract data as required for the summary.
"""
import collections
import contextlib
import itertools
import logging
import operator
from django.conf import settings

from django.utils.translation import ugettext_lazy as _

from configuration.configuration import QuestionnaireQuestion, \
    QuestionnaireSubcategory, QuestionnaireQuestiongroup
from configuration.configured_questionnaire import ConfiguredQuestionnaire
from configuration.models import Value
from qcat.errors import ConfigurationError
from questionnaire.models import Questionnaire
from questionnaire.templatetags.questionnaire_tags import get_static_map_url

logger = logging.getLogger(__name__)


class QuestionnaireParser(ConfiguredQuestionnaire):
    """
    Get only data which is configured to appear in the summary. This is defined
    by the configuration-field: 'summary', which specifies the section
    of the summary for given field for the chosen summary-config (e.g. 'full',
    'one page', 'four page').
    """

    def __init__(self, config, summary_type: str, n_a: str,
                 questionnaire: Questionnaire, **data):
        self.summary_type = summary_type
        self.data = {}
        self.n_a = n_a
        self.config_object = config
        super().__init__(questionnaire=questionnaire, config=config, **data)

    def put_question_data(self, child: QuestionnaireQuestion):
        """
        Put the value to self.data, using the name as defined in the config
        ('summary': {'this_type': <key_name>}}.
        As some key names are duplicated by virtue (config may use the same
        question twice), but represent different and important content, some
        keys are overridden with the help of the questions questiongroup.

        This cannot be solved on the config as the same question is listed
        twice, so the key-name overriding setting must be ready for versioning.
        """
        if child.summary and self.summary_type in child.summary['types']:
            options = {
                **child.summary['default'],
                **child.summary.get(self.summary_type, {})
            }
            if 'field_name' not in options:
                raise ConfigurationError(
                    'At least a unique field name must be set for "summary" '
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
            return {'img_url': '', 'coordinates': []}
        else:
            return {
                'img_url': get_static_map_url(self.questionnaire),
                'coordinates': [
                    '{}, {}'.format(round(coords[0], 5), round(coords[1], 5))
                    for coords in self.questionnaire.geom.coords
                ]
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
            if settings.DEBUG:
                logger.warning('No or more than one list of values is set for '
                               '{keyword}'.format(keyword=child.keyword))
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
            'questiongroup_conditions', []
        )
        # ..and split the strings to a more usable dict.
        nested_elements = dict(self.split_raw_children(*nested_elements_config))

        for value in selected:
            child_text = '{title} - '.format(title=value[0])
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
                        if child_value:
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

    def _get_qg_selected_value(self, child: QuestionnaireQuestion,
                               all_values=False, index=0):
        values = {}
        with contextlib.suppress(IndexError):
            values = self.values.get(child.questiongroup.keyword, [])[index]
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
        if isinstance(values, str):
            text = values
        else:
            text = ', '.join([choices_labels[choice] for choice in values])

        text_parts = dict(
            label='{}: '.format(child_question.label) if has_label else '',
            multi_line='<br>' if selected_child_len > 1 else '',
            text=text,
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
        has_content = False
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
                if not values:
                    continue

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
                has_content = True

        return table if has_content else {}

    def get_questiongroups_in_table(self, section: QuestionnaireSubcategory):
        """
        Get only questiongroups that are configured to be shown in the table.
        """
        used = list(itertools.chain(*section.table_grouping))
        for questiongroup in section.questiongroups:
            if questiongroup.keyword in used:
                yield questiongroup

    def get_qg_values_with_label_scale(self, child: QuestionnaireQuestion):
        items = []
        for group in child.questiongroup.parent_object.questiongroups:
            values = self._get_qg_selected_value(group.children[0], all_values=True)

            # 'other' values have no choices.
            if group.questions[0].choices:
                label = group.label
                selected_question = 0
                text_question = 1
            else:
                group_values = self.values.get(group.keyword)
                if not group_values:
                    continue
                label = group_values[0].get(group.questions[0].keyword)
                selected_question = 1
                text_question = 2

            value = values.get(group.questions[selected_question].keyword)
            if not value:
                continue

            items.append({
                'label': label,
                'range': range(0, len(group.questions[selected_question].choices)),
                'selected':  list(dict(group.questions[selected_question].choices).keys()).index(value),
                'text': values.get(group.questions[text_question].keyword)
            })
        return {
            "labels": dict(child.questiongroup.questions[0].choices).values(),
            "items2": items
        }


class TechnologyParser(QuestionnaireParser):
    """
    Specific methods for technologies.
    """

    def get_human_env_access(self, child: QuestionnaireQuestion):
        # e.g. 5.9 - get all info from parent questiongroup
        # combine children from questiongroup with 'other'
        children = itertools.chain(
            *[qg.children for qg in child.questiongroup.parent_object.questiongroups]
        )
        for child in children:
            try:
                value = int(self._get_qg_selected_value(child))
            except (ValueError, TypeError):
                continue

            if not child.keyword.startswith('tech_access_other_'):
                # defined fields
                yield from self._qg_scale_format(
                    child=child,
                    value=value,
                    label_left=child.choices[0][1],
                    label_right=child.choices[-1][1]
                )
            elif child.keyword == 'tech_access_other_measure':
                # 'other'
                yield from self._qg_scale_format(
                    child=child,
                    label=self._get_qg_selected_value(
                        child, all_values=True
                    ).get('tech_access_other_specify'),
                    value=value,
                    label_left=child.choices[0][1],
                    label_right=child.choices[-1][1]
                )

    def get_tech_costbenefit(self, child: QuestionnaireQuestion):
        # e.g. 6.4. - all info from radio buttons
        values = self._get_qg_selected_value(child, all_values=True)

        for child in child.questiongroup.children:
            str_value = values.get(child.keyword, '')
            # in the template, the numeric position of the value in the
            # 'range' is required.
            try:
                choice_keys = dict(child.choices).keys()
                value = list(choice_keys).index(str_value) + 1
            except ValueError:
                continue

            yield from self._qg_scale_format(
                child=child,
                value=value,
                label_left=child.choices[0][1],
                label_right=child.choices[-1][1]
            )

    def get_impact(self, child: QuestionnaireQuestion, has_siblings: False):
        """
        The last block (off-site impacts) has no siblings, all other blocks
        have nested questiongroups.
        Also, as 'other' may be repeating, 'other_spefify' is in a loop as well.
        Sorry!
        """
        if has_siblings:
            categories = child.questiongroup.parent_object.parent_object.subcategories
            questiongroups = itertools.chain(
                *[category.questiongroups for category in categories]
            )
        else:
            questiongroups = child.questiongroup.parent_object.questiongroups

        for group in questiongroups:
            if len(group.children) < 3:
                # omit 'tech_specify'
                continue
            if group.children[0].keyword == 'tech_impacts_other_specify':
                for items in self.values.get(group.keyword, []):
                    value_child = 2
                    label = items.get(group.children[0].keyword)
                    value = items.get(group.children[value_child].keyword)
                    label_left = items.get(group.children[1].keyword)
                    label_right = items.get(group.children[3].keyword)
                    before_label = group.children[4].label
                    before_value = items.get(group.children[4].keyword)
                    after_label = group.children[5].label
                    after_value = items.get(group.children[5].keyword)
                    comment_value = items.get(group.children[6].keyword)
                    yield from self._get_impact_row(
                        child=group.children[value_child], label=label,
                        value=value, label_left=label_left,
                        label_right=label_right, before_value=before_value,
                        before_label=before_label, after_value=after_value,
                        after_label=after_label, comment_value=comment_value
                    )
            else:
                value_child = 0
                label = group.children[value_child].label
                value = self._get_qg_selected_value(group.children[value_child])
                label_left = group.children[0].additional_translations.get('label_left')
                label_right = group.children[0].additional_translations.get('label_right')
                before_label = group.children[1].label
                before_value = self._get_qg_selected_value(group.children[1])
                after_label = group.children[2].label
                after_value = self._get_qg_selected_value(group.children[2])
                comment_value = self._get_qg_selected_value(group.children[3])
                yield from self._get_impact_row(
                    child=group.children[value_child], label=label,
                    value=value, label_left=label_left, label_right=label_right,
                    before_value=before_value, before_label=before_label,
                    after_value=after_value, after_label=after_label,
                    comment_value=comment_value,
                )

    def _get_impact_row(self, child: QuestionnaireQuestion, label: str,
                        value: int, label_left: str, label_right: str,
                        before_value: str, before_label: str, after_value: str,
                        after_label: str, comment_value: str):
        if value and isinstance(value, int):
            comment = ''
            if before_value or after_value:
                comment = f'{before_label}: {before_value}\n{after_label}: {after_value}'

            # if a comment is set, add it
            if comment_value:
                comment += '\n' + (comment_value or '')

            yield from self._qg_scale_format(
                child=child,
                value=value,
                label=label,
                label_left=label_left,
                label_right=label_right,
                comment=comment
            )

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
        Create elements for a single line. The structure of questions varies
        between all elements, regarding number of questions and content/scale of
        questions.
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
                    collections.OrderedDict(question.choices).keys()
                )
                with contextlib.suppress(ValueError):
                    choice_keys.remove('')
                    choice_keys.remove('cope_unknown')

                value = values.get(question.keyword)
                if value not in choice_keys:
                    string_value = dict(question.choices).get(value)
                    if string_value:
                        comment += _(' Answer: {}').format(string_value)
                else:
                    value = choice_keys.index(value)

            else:
                # All other fields, such as 'season' go into the comments.
                comment_key = values.get(question.keyword)
                if not group.label.startswith('other'):
                    comment_key = dict(question.choices).get(comment_key)
                if comment_key:
                    comment += '{label}: {value}'.format(
                        label=question.label,
                        value=comment_key
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


class ApproachParser(QuestionnaireParser):
    """
    Specific methods for approaches
    """

    def get_aims_enabling(self, child: QuestionnaireQuestion, name: str):
        """
        Get enabling/hindering values only.
        """
        field_name = 'app_condition_{}_specify'.format(name)
        for group in child.questiongroup.parent_object.questiongroups:
            try:
                text = self.values[group.keyword][0][field_name]
            except (KeyError, IndexError):
                continue

            yield group.label, text

    def get_stakeholders_roles(self, child: QuestionnaireQuestion):
        groups = child.questiongroup.parent_object.questiongroups
        # the first element in the group contains the labels of the selected
        # questiongroups, so get the values.
        label_values = self.values.get(groups[0].keyword)
        if not label_values:
            return
        labels = label_values[0].get('app_stakeholders')

        # use only groups that are selected (i.e. in the labels-list)
        selected_group_keywords = [
            group.keyword for group in groups
            if group.view_options.get('conditional_question') in labels
        ]
        first_children = self.config_object.get_questiongroup_by_keyword(
            selected_group_keywords[0]
        ).children
        # Get the headers first.
        yield from self._get_stakeholder_row(
            label=groups[0].children[0].label,
            app_stakeholders_roles=first_children[0].label,
            app_stakeholders_comments=first_children[1].label
        )

        for index, group_keyword in enumerate(selected_group_keywords):
            # Always display translated label ('NGO', 'local land users')
            label = Value.objects.get(keyword=labels[index]).get_translation(
                keyword='label', configuration='approaches'
            )
            # If additional info is specified (role, specify), append this.
            values = self.values[group_keyword][0] if group_keyword in self.values else {}

            yield from self._get_stakeholder_row(label=label, **values)

        # Also include 'other' stakeholders
        other_group = next(group for group in groups if group.children[0].keyword == 'app_stakeholders_other')
        other = self.values.get(other_group.keyword, [])
        if other and len(other) == 1 and 'app_stakeholders_other' in other[0]:
            values = other[0]
            yield from self._get_stakeholder_row(
                label=values[other_group.children[0].keyword], **values
            )

    def _get_stakeholder_row(self, label: str, **kwargs):
        roles = kwargs.get('app_stakeholders_roles')
        comments = kwargs.get('app_stakeholders_comments')
        yield label, comments or '', roles or ''

    def get_involvement(self, child: QuestionnaireQuestion):
        for qg in child.questiongroup.parent_object.questiongroups:
            try:
                comment = self.values[qg.keyword][0]['app_involvement_who']
            except (KeyError, IndexError):
                comment = ''

            yield {
                'title': qg.label,
                'comment': comment,
                'items': self.get_full_range_values(qg.questions[0])
            }

    def get_highlight_element(self, child: QuestionnaireQuestion):
        return {
            'highlighted': bool(self._get_qg_selected_value(child) == 1),
            'text': child.questiongroup.parent_object.label
        }

    def get_highlight_element_with_text(self, child: QuestionnaireQuestion):
        """
        Really specific method for question 4.3.
        """
        selected = self._get_qg_selected_value(child)
        return {
            'value': self.get_full_range_values(child),
            'bool': {
                'highlighted': selected and selected != 'app_institutions_no',
                'text': child.questiongroup.parent_object.label
            }
        }

    def get_financing_subsidies(self, child: QuestionnaireQuestion):
        """
        Get the 'selected' questiongroups from the questiongroups condition
        and build a scale with vertical label from it.
        Also, the 'is_subsidised' info for the first element in the financing
        part is gathered.
        The structure is very nested and complex, but follows the config.
        """
        none_selected = 'app_subsidies_inputs_none'
        other_question = 'app_subsidies_inputs_other'
        selected_groups = self._get_qg_selected_value(child) or []
        nested_elements_config = child.form_options.get('questiongroup_conditions') or []
        # A dict with the mapping of questiongroup-name and identifier.
        nested_elements = dict(self.split_raw_children(*nested_elements_config))
        labels = dict(child.choices)
        items = []

        # Prepare 'other' questiongroup if filled in (usually the last question)
        for questiongroup in reversed(child.questiongroup.parent_object.questiongroups):
            if other_question in [question.keyword for question in questiongroup.questions]:
                if self.values.get(questiongroup.keyword):
                    selected_groups.append(questiongroup.keyword)
                    nested_elements[questiongroup.keyword] = questiongroup.keyword
                    labels[questiongroup.keyword] = self.values[questiongroup.keyword][0][other_question]
                break

        for group in selected_groups:
            # Skip the group for 'none'
            if group == none_selected:
                continue

            qg = self.config_object.get_questiongroup_by_keyword(
                nested_elements[group]
            )
            label = labels[group]
            columns = qg.form_options.get('table_columns', 3)
            try:
                row = self.get_subsidies_row(qg, **self.values[qg.keyword][0])
            except (KeyError, IndexError):
                continue

            # if there are only two columns, there is no additional label.
            if columns == 2:
                items.append(row.make_row(label, 0, 1))
            else:
                # split questions into rows according to defined columns.
                index = 0
                while index + columns <= len(qg.questions):
                    if qg.questions[index + 1].keyword in row.values:
                        # 'other' / custom labels: label text is set as value.
                        if qg.questions[index].keyword.endswith('other'):
                            label = row.values[qg.questions[index].keyword]
                        else:
                            label = f'{label}: {qg.questions[index].choices[0][1]}'

                        items.append(
                            row.make_row(
                                label=label,
                                selected=index + 1,
                                text=index + 2
                            )
                        )
                    index += columns

        return {
            "is_subsidised": {
                "highlighted": selected_groups and none_selected not in selected_groups,
                "text": _("Subsidies for specific inputs")
            },
            "subsidies": {
                "title": child.questiongroup.parent_object.label,
                "items": items
            }
        }

    def get_subsidies_row(self, questiongroup, **values):

        class SubsidiesRow:

            def __init__(self, questiongroup, **values):
                self.qg = questiongroup
                self.values = values
                self.labels = None

            def make_row(self, label, selected, text):
                self.labels = dict(self.qg.questions[selected].choices)
                return {
                    'label': label,
                    'range': range(0, len(self.labels)),
                    'selected': list(self.labels.keys()).index(values.get(self.qg.questions[selected].keyword)),
                    'text': values.get(self.qg.questions[text].keyword) or '',
                    'scale': self.labels.values()
                }

        return SubsidiesRow(questiongroup, **values)

    def get_impacts_motivation(self, child: QuestionnaireQuestion):
        selected_values = self.values.get(child.questiongroup.keyword)
        if not selected_values:
            return
        selected = selected_values[0].get(child.keyword)
        for keyword, label in dict(child.choices).items():
            yield {
                'highlighted': keyword in selected,
                'text': label
            }

    def get_impacts(self, child: QuestionnaireQuestion):

        for qg in child.questiongroup.parent_object.questiongroups:
            selected = self._get_qg_selected_value(qg.questions[0])
            if not selected:
                continue

            # no choices = this is an 'other' input
            if not qg.questions[0].choices:
                label = selected
                selected = self._get_qg_selected_value(qg.questions[1])
                select = 1
                text = 2
            else:
                # this works for english only. discussed and okey-d.
                label = qg.questions[0].label
                select = 0
                text = 1

            yield {
                'label': label,
                'range': range(0, len(qg.questions[select].choices)),
                'selected': selected - 1 if selected else None,
                'text': self._get_qg_selected_value(qg.questions[text]) or '',
                'scale': dict(qg.questions[select].choices).values()
            }

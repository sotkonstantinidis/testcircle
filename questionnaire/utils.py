import ast
from django.core.urlresolvers import reverse
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _, get_language
from django.utils.dateparse import parse_datetime

from configuration.configuration import (
    QuestionnaireQuestion,
)
from configuration.utils import get_or_create_configuration
from qcat.errors import QuestionnaireFormatError


def clean_questionnaire_data(data, configuration):
    """
    Clean a questionnaire data dictionary so it can be saved to the
    database. This namely removes all empty values and parses measured
    values to integers.

    This function can also be used to test if a questionnaire data
    dictionary is empty (if returned cleaned data = {}).

    Args:
        ``data`` (dict): A questionnaire data dictionary.

        ``configuration``
        (:class:`configuration.configuration.QuestionnaireConfiguration`):
        The configuration of the questionnaire to test the data against.

    Returns:
        ``dict``. The cleaned questionnaire data dictionary.

        ``list``. A list with errors encountered. Empty if the
        dictionary is valid.
    """
    errors = []
    cleaned_data = {}
    try:
        is_valid_questionnaire_format(data)
    except QuestionnaireFormatError as e:
        return cleaned_data, [str(e)]
    """
    Collect the questiongroup conditions. This can be done only once for
    all questiongroups for performance reasons.
    The conditions are collected in a dict of form:
    {
        "CONDITION_NAME": ("QG_KEYWORD", "Q_KEYWORD", ["COND_1", "COND_2"])
    }
    """
    questiongroup_conditions = {}
    for questiongroup in configuration.get_questiongroups():
        for question in questiongroup.questions:
            for conditions in question.questiongroup_conditions:
                condition, condition_name = conditions.split('|')
                if condition_name in questiongroup_conditions:
                    questiongroup_conditions[condition_name][2].append(
                        condition)
                else:
                    questiongroup_conditions[condition_name] = \
                        questiongroup.keyword, question.keyword, [condition]
    for qg_keyword, qg_data_list in data.items():
        questiongroup = configuration.get_questiongroup_by_keyword(qg_keyword)
        if questiongroup is None:
            errors.append(
                'Questiongroup with keyword "{}" does not exist'.format(
                    qg_keyword))
            continue
        if questiongroup.max_num < len(qg_data_list):
            errors.append(
                'Questiongroup with keyword "{}" has a max_num of {} but '
                'appears {} times'.format(
                    qg_keyword, questiongroup.max_num, len(qg_data_list)))
            continue
        cleaned_qg_list = []
        for qg_data in qg_data_list:
            cleaned_qg = {}
            for key, value in qg_data.items():
                if not value and not isinstance(value, (bool, int)):
                    continue
                question = questiongroup.get_question_by_key_keyword(key)
                if question is None:
                    errors.append(
                        'Question with keyword "{}" is not valid for '
                        'Questiongroup with keyword "{}"'.format(
                            key, qg_keyword))
                    continue
                if question.conditional:
                    for q in question.questiongroup.questions:
                        for c in q.conditions:
                            if key in c[2]:
                                cond_data = qg_data.get(q.keyword)
                                if not cond_data or c[0] not in cond_data:
                                    errors.append(
                                        'Key "{}" is only valid if "{}={}"'
                                        .format(key, q.keyword, c[0]))
                if question.field_type in ['measure']:
                    try:
                        value = int(value)
                    except ValueError:
                        errors.append(
                            'Measure value "{}" of key "{}" (questiongroup '
                            '"{}") is not valid.'.format(
                                value, key, qg_keyword))
                        continue
                if question.field_type in ['bool', 'measure', 'select_type']:
                    if value not in [c[0] for c in question.choices]:
                        errors.append(
                            'Value "{}" is not valid for key "{}" ('
                            'questiongroup "{}").'.format(
                                value, key, qg_keyword))
                        continue
                elif question.field_type in ['checkbox', 'image_checkbox']:
                    if not isinstance(value, list):
                        errors.append(
                            'Value "{}" of key "{}" needs to be a list'.format(
                                value, key))
                        continue
                    for v in value:
                        if v not in [c[0] for c in question.choices]:
                            errors.append(
                                'Value "{}" is not valid for key "{}" ('
                                'questiongroup "{}").'.format(
                                    value, key, qg_keyword))
                            continue
                elif question.field_type in ['char', 'text']:
                    if not isinstance(value, dict):
                        errors.append(
                            'Value "{}" of key "{}" needs to be a dict.'
                            .format(value, key))
                        continue
                    translations = {}
                    for locale, translation in value.items():
                        if translation:
                            if (question.max_length and
                                    len(translation) > question.max_length):
                                errors.append(
                                    'Value "{}" of key "{}" exceeds the '
                                    'max_length of {}.'.format(
                                        translation, key, question.max_length))
                                continue
                            translations[locale] = translation
                    value = translations
                elif question.field_type in ['image']:
                    pass
                else:
                    raise NotImplementedError(
                        'Field type "{}" needs to be checked properly'.format(
                            question.field_type))
                if value or isinstance(value, (bool, int)):
                    cleaned_qg[key] = value
            if cleaned_qg:
                cleaned_qg_list.append(cleaned_qg)
        if cleaned_qg_list:
            cleaned_data[qg_keyword] = cleaned_qg_list
        if cleaned_qg_list and questiongroup.questiongroup_condition:
            condition_fulfilled = False
            for condition_name, condition_data in questiongroup_conditions.\
                    items():
                if condition_name != questiongroup.questiongroup_condition:
                    continue
                for qg_data in data.get(condition_data[0], []):
                    condition_value = qg_data.get(condition_data[1])
                    if isinstance(condition_value, list):
                        all_values_evaluated = False
                        for cond_value in condition_value:
                            evaluated = True
                            for c in condition_data[2]:
                                try:
                                    evaluated = evaluated and eval(
                                        '{}{}'.format(cond_value, c))
                                except NameError:
                                    evaluated = evaluated and eval(
                                        '"{}"{}'.format(cond_value, c))
                                except:
                                    evaluated = False
                                    continue
                            all_values_evaluated = (
                                all_values_evaluated or evaluated)
                        condition_fulfilled = (
                            condition_fulfilled or all_values_evaluated)
                    else:
                        evaluated = True
                        for c in condition_data[2]:
                            try:
                                evaluated = evaluated and eval('{}{}'.format(
                                    condition_value, c))
                            except:
                                evaluated = False
                                continue
                        condition_fulfilled = evaluated or condition_fulfilled
            if condition_fulfilled is False:
                errors.append(
                    'Questiongroup with keyword "{}" requires condition "{}".'.
                    format(
                        questiongroup.keyword,
                        questiongroup.questiongroup_condition))
    return cleaned_data, errors


def is_valid_questionnaire_format(questionnaire_data):
    """
    Helper function to check if the data of a questionnaire is valid or
    not.

    Args:
        ``questionnaire_data`` (dict): A questionnaire data dictionary.

    Returns:
        ``bool``. ``True`` if the dictionary is a valid questionnaire
        data.

    Raises:
        ``qcat.errors.QuestionnaireFormatError``
    """
    if not isinstance(questionnaire_data, dict):
        raise QuestionnaireFormatError(questionnaire_data)
    for k, v in questionnaire_data.items():
        if not isinstance(v, list):
            raise QuestionnaireFormatError(questionnaire_data)
    return True


def get_questionnaire_data_in_single_language(questionnaire_data, locale):
    """
    Returns a questionnaire data dictionary in a single language. For
    translated values, the dictionary value containing the translations
    is replaced by a single string value with the translation in the
    given language.

    Example::

        # Input:
        {
          "qg_1": [
            {
              "key": {
                "en": "value_en",
                "es": "value_es"
              }
            }
          ]
        }

        # Output with locale=es
        {
          "qg_1": [
            {
              "key": "value_es"
            }
          ]
        }

    Args:
        ``questionnaire_data`` (dict): A questionnaire data dictionary.

        ``locale`` (str): The locale to find the translations for.

    Returns:
        ``dict``. The questionnaire data dictionary, without
        translations.
    """
    is_valid_questionnaire_format(questionnaire_data)
    data_sl = {}
    for questiongroup_keyword, questiongroups in questionnaire_data.items():
        qg_sl = []
        for questiongroup_data in questiongroups:
            qg_data_sl = {}
            for key, value in questiongroup_data.items():
                if isinstance(value, dict):
                    qg_data_sl[key] = value.get(locale)
                else:
                    qg_data_sl[key] = value
            qg_sl.append(qg_data_sl)
        data_sl[questiongroup_keyword] = qg_sl
    return data_sl


def get_questionnaire_data_for_translation_form(
        questionnaire_data, current_locale, original_locale):
    """
    Returns a questionnaire data dictionary which can be used in the
    form for translation. Each translated value is replaced by three keys:

    1. ``{"old_key": {...}}``: Contains all existing translations
    2. ``{"translation_key": "value"}``: Contains the translation in the
       current locale
    3. ``{"original_key": "value"}``: Contains the value as it was first
       entered in the original local.

    Example::

        # Input
        {
          "qg_1": [
            {
              "key_1": {
                "en": "value_en",
                "es": "value_es"
              }
            }
          ]
        }

        # Output with original_locale=en and current_locale=es
        {
          "qg_1": [
            {
              "old_key_1": {
                "en": "value_en",
                "es": "value_es"
              },
              "translation_key_1": "value_es",
              "original_key_1": "value_en"
            }
          ]
        }

    Args:
        ``questionnaire_data`` (dict): A questionnaire data dictionary.

        ``current_locale`` (str): The currently active locale.

        ``original_locale`` (str): The original locale in which the
        values were entered.

    Returns:
        ``dict``. The questionnaire data dictionary, with additional
        translation form fields.
    """
    is_valid_questionnaire_format(questionnaire_data)
    translation_prefix = QuestionnaireQuestion.translation_translation_prefix
    original_prefix = QuestionnaireQuestion.translation_original_prefix
    old_prefix = QuestionnaireQuestion.translation_old_prefix
    if original_locale is None:
        original_locale = current_locale
    data_translation = {}
    for questiongroup_keyword, questiongroups in questionnaire_data.items():
        qg_translation = []
        for questiongroup_data in questiongroups:
            qg_data_translation = {}
            for key, value in questiongroup_data.items():
                if isinstance(value, dict):
                    qg_data_translation['{}{}'.format(
                        translation_prefix, key)] = value.get(current_locale)
                    qg_data_translation['{}{}'.format(
                        original_prefix, key)] = value.get(original_locale)
                    qg_data_translation['{}{}'.format(old_prefix, key)] = value
                else:
                    qg_data_translation[key] = value
            qg_translation.append(qg_data_translation)
        data_translation[questiongroup_keyword] = qg_translation
    return data_translation


def get_questiongroup_data_from_translation_form(
        questiongroup_data, current_locale, original_locale):
    """
    Returns a cleaned questiongroup data dictionary from a dict in the
    translation form format. New translations will overwrite old
    translations stored in the hidden field.

    .. seealso::
        :func:`get_questionnaire_data_for_translation_form` for the
        format of the translation form dictionary.

    Args:
        ``questiongroup_data`` (dict): A data dictionary of a single
        questiongroup.

        ``current_locale`` (str): The currently active locale.

        ``original_locale`` (str): The original locale in which the
        values were entered.

    Returns:
        ``dict``. The questiongroup data dictionary with translations as
        it can be stored in the database.
    """
    translation_prefix = QuestionnaireQuestion.translation_translation_prefix
    original_prefix = QuestionnaireQuestion.translation_original_prefix
    old_prefix = QuestionnaireQuestion.translation_old_prefix
    if original_locale is None:
        original_locale = current_locale

    questiongroup_data_cleaned = {}
    # Collect the old translations and parse them to a dict
    for key, value in questiongroup_data.items():
        if not key.startswith(old_prefix):
            continue
        k = key.replace(old_prefix, '')
        try:
            questiongroup_data_cleaned[k] = ast.literal_eval(value)
        except:
            questiongroup_data_cleaned[k] = value

    # Collect the originals and translations and update the old
    # translations
    for key, value in questiongroup_data.items():
        if key.startswith(old_prefix):
            continue
        if key.startswith(translation_prefix):
            k = key.replace(translation_prefix, '', 1)
            if not isinstance(questiongroup_data_cleaned[k], dict):
                questiongroup_data_cleaned[k] = {}
            questiongroup_data_cleaned[k].update({current_locale: value})
        elif key.startswith(original_prefix):
            k = key.replace(original_prefix, '', 1)
            if not isinstance(questiongroup_data_cleaned[k], dict):
                questiongroup_data_cleaned[k] = {}
            questiongroup_data_cleaned[k].update({original_locale: value})
        else:
            questiongroup_data_cleaned[key] = value

    return questiongroup_data_cleaned


def get_active_filters(questionnaire_configuration, query_dict):
    """
    Get the currently active filters based on the query dict (eg. from
    the request). Only valid filters (correct format, based on
    questiongroups and keys of current configuration) are respected.
    The query dict can contain multiple keys with the same names.

    The current format of a filter is::

        filter__[questiongroup]__[key]=[value]

    Example::

        filter__qg_11__key_14=value_14_1

    Some filters can also be set with a different format. These are:

    * ``q``: A search term for the full text search (``q=search``)

    All the options can also be combined, such as::

        q=search&filter__qg_11__key_14=value_14_1

    Args:
        ``questionnaire_configuration``
        (:class:`configuration.configuration.QuestionnaireConfiguration`):
        The questionnaire configuration.

        ``query_dict`` (Nested Multidict): A nested multidict object,
        eg. ``request.GET``.

    Returns:
        ``list``. A list of dictionaries with the active and valid
        filters. Each dictionary contains the following entries:

        - ``questiongroup``: The keyword of the questiongroup. For
          ``q``, this is set to ``_search``.

        - ``key``: The keyword of the key. For ``q``, this is set to
          ``_search``.

        - ``key_label``: The label of the key. For ``q``, this is set to
          "Search Terms".

        - ``value``: The keyword of the value.

        - ``value_label``: The label of the value if available. Else the
          value as provided in the filter is returned.

        - ``type``: The field type of the key. For ``q``, this is set to
          ``_search``.
    """
    active_filters = []
    for filter_param, filter_values in query_dict.lists():

        if filter_param == 'q':
            for filter_value in filter_values:
                active_filters.append({
                    'type': '_search',
                    'key': '_search',
                    'key_label': _('Search Terms'),
                    'value': filter_value,
                    'value_label': filter_value,
                    'questiongroup': '_search',
                })
            continue

        if not filter_param.startswith('filter__'):
            continue

        params = filter_param.split('__')
        if len(params) != 3:
            continue

        filter_questiongroup = params[1]
        filter_key = params[2]

        question = questionnaire_configuration.get_question_by_keyword(
            filter_questiongroup, filter_key)

        if question is None:
            continue

        for filter_value in filter_values:
            value_label = next(
                (v[1] for v in question.choices if v[0] == filter_value),
                filter_value)

            active_filters.append({
                'questiongroup': filter_questiongroup,
                'key': filter_key,
                'key_label': question.label,
                'value': filter_value,
                'value_label': value_label,
                'type': question.field_type,
            })

    return sorted(active_filters, key=lambda k: k['key'])


def get_link_data(linked_objects, link_configuration_code=None):
    """
    Return a data representation (to be stored in the session or used in
    forms) of links retrieved from the database.

    Args:
        ``linked_objects`` (list of questionnaire.models.Questionnaire):
        A list of database model objects representing the linked
        Questionnaires.

    Kwargs:
        ``link_configuration_code`` (str): Optionally provide a
        configuration keyword for the link. If none is provided, the
        configuration is derived from the Questionnaire object.

    Returns:
        ``dict``. A dictionary containing the links grouped by
        link_configuration_code. The basic form of the dictionary is as
        follows::

            {
              "sample": [
                {
                  "id": 1,
                  "display": "This is a link to Questionnaire with ID 1",
                  "form_display": "Name of Questionnaire with ID 1"
                }
              ]
            }
    """
    link_configurations = {}
    links = {}
    for link in linked_objects:
        if link_configuration_code is None:
            # TODO: This does not handle questionnaires with multiple
            # configurations correctly
            link_configuration_code = link.configurations.first().code
        link_configuration, link_configurations = get_or_create_configuration(
            link_configuration_code, link_configurations)
        link_display = get_link_display(link, link_configuration)
        link_list = links.get(link_configuration_code, [])
        link_name = link_configuration.get_questionnaire_name(
            get_questionnaire_data_in_single_language(
                link.data, get_language()))
        link_list.append({
            'id': link.id,
            'display': link_display,
            'form_display': link_name,
        })
        links[link_configuration_code] = link_list
    return links


def get_link_display(link_object, link_configuration):
    """
    Return the representation of a linked questionnaire used for display
    of the link. The display representation is the rendered template (
    ``/questionnaire/partial/link.html``) specific to the given
    configuration.

    Args:
        ``link_object`` (questionnaire.models.Questionnaire): The
        database model object of the linked Questionnaire.

        ``link_configuration`` (
        configuration.configuration.QuestionnaireConfiguration): The
        Configuration object of the linked Questionnaire.

    Returns:
        ``str``. The display representation of the link as rendered
        HTML.
    """
    link_data = link_configuration.get_list_data([link_object.data])
    link_template = '{}/questionnaire/partial/link.html'.format(
        link_configuration.keyword)
    link_route = '{}:questionnaire_details'.format(link_configuration.keyword)
    return render_to_string(link_template, {
        'link_data': link_data[0],
        'link_url': reverse(link_route, args=(link_object.id,))
    })


def get_list_values(
        configuration_code=None, es_search={}, questionnaire_objects=[]):
    """
    Retrieves and prepares data to be used in a list representation.
    Either handles a list of questionnaires retrieved from the database
    or searched with Elasticsearch.

    Kwargs:
        ``configuration_code`` (str): Optionally provide a configuration
        code which will be used for all items. This may result in some
        items not displaying any data if they are not shown in one of
        their configurations. If set to ``None``, the original
        configuration for each questionnaire is used to collect the list
        values.

        ``es_search`` (dict): A dictionary as retrieved from an
        Elasticsearch query.

        ``questionnaire_objects`` (list): A list (queryset) of
        :class:`questionnaire.models.Questionnaire` models retrieved
        from the database.

    Returns:
        ``list``. A list of dictionaries containing the values needed
        for the list representation of Questionnaires. Along the values
        specified in the settings to appear in the list, some metadata
        is returned for each entry.
    """
    list_entries = []

    for result in es_search.get('hits', {}).get('hits', []):
        # Results from Elasticsearch. List values are already available.

        # TODO: Fall back to the original configuration
        if configuration_code is None:
            configuration_code = 'sample'

        template_value = result.get('_source', {}).get('list_data', {})
        for key, value in template_value.items():
            if isinstance(value, dict):
                # TODO: Fall back to the original language
                template_value[key] = value.get('en')

        source = result.get('_source', {})
        configurations = source.get('configurations', [])

        template_value.update({
            'configuration': configuration_code,  # Used for rendering
            'id': result.get('_id'),
            'configurations': configurations,
            'native_configuration': configuration_code in configurations,
            'created': parse_datetime(
                source.get('created', '')),
            'updated': parse_datetime(
                source.get('updated', '')),
        })
        list_entries.append(template_value)

    questionnaire_configurations = {}
    for obj in questionnaire_objects:
        # Results from database query. List values have to be retrieved
        # through the configuration of the questionnaires.

        # TODO: Fall back to the original configuration
        if configuration_code is None:
            configuration_code = 'sample'

        questionnaire_configuration, questionnaire_configurations = \
            get_or_create_configuration(
                configuration_code, questionnaire_configurations)

        template_value = questionnaire_configuration.get_list_data(
            [obj.data])[0]
        for key, value in template_value.items():
            if isinstance(value, dict):
                # TODO: Fall back to the original language
                template_value[key] = value.get('en')

        configurations = [conf.code for conf in obj.configurations.all()]

        template_value.update({
            'configuration': configuration_code,  # Used for rendering
            'id': obj.id,
            'configurations': configurations,
            'native_configuration': configuration_code in configurations,
            'created': obj.created,
            'updated': obj.updated,
        })
        list_entries.append(template_value)

    return list_entries

import ast

from configuration.configuration import QuestionnaireQuestion
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
        cleaned_qg_list = []
        for qg_data in qg_data_list:
            cleaned_qg = {}
            for key, value in qg_data.items():
                if not value and not isinstance(value, bool):
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
                            translations[locale] = translation
                    value = translations
                elif question.field_type in ['image']:
                    pass
                else:
                    raise NotImplementedError(
                        'Field type "{}" needs to be checked properly'.format(
                            question.field_type))
                if value or isinstance(value, bool):
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

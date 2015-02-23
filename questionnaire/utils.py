import ast

from configuration.configuration import QuestionnaireQuestion
from qcat.errors import QuestionnaireFormatError
from qcat.utils import is_empty_list_of_dicts


def is_empty_questionnaire(questionnaire_data):
    """
    Helper function to check if the data of a questionnaire is empty,
    e.g. does not contain any values. Entries such as [{}] are
    considered as empty.

    Args:
        ``questionnaire_data`` (dict): A questionnaire data dictionary.

    Returns:
        ``bool``. ``True`` if the dictionary is empty or contains only
        empty values, ``False`` otherwise.

    Raises:
        ``qcat.errors.QuestionnaireFormatError``
    """
    is_valid_questionnaire_format(questionnaire_data)
    for k, v in questionnaire_data.items():
        if v == [{}]:
            continue
        if not is_empty_list_of_dicts(v):
            return False
    return True


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
            k = key.replace(translation_prefix, '')
            if not isinstance(questiongroup_data_cleaned[k], dict):
                questiongroup_data_cleaned[k] = {}
            questiongroup_data_cleaned[k].update({current_locale: value})
        elif key.startswith(original_prefix):
            k = key.replace(original_prefix, '')
            if not isinstance(questiongroup_data_cleaned[k], dict):
                questiongroup_data_cleaned[k] = {}
            questiongroup_data_cleaned[k].update({original_locale: value})
        else:
            questiongroup_data_cleaned[key] = value

    return questiongroup_data_cleaned

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

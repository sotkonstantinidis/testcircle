from datetime import datetime
from django.conf import settings
from importlib import import_module
session_store = import_module(settings.SESSION_ENGINE).SessionStore()


def find_dict_in_list(list_, key, value, not_found={}):
    """
    A helper function to find a dict based on a given key and value pair
    inside a list of dicts. Only the first occurence is returned if
    there are multiple dicts with the key and value.

    Args:
        ``list_`` (list): A list of dicts to search in.

        ``key`` (str): The key of the dict to look at.

        ``value`` (str): The value of the key the dict has to match.

    Kwargs:
        ``not_found`` (dict): The return value if no dict was found.
        Defaults to ``{}``.

    Returns:
        ``dict``. The dict if found. If not found, the return value as
        provided is returned or an empty dict by default.
    """
    if value is not None:
        for el in list_:
            if el.get(key) == value:
                return el
    return not_found


def is_empty_list_of_dicts(list_):
    """
    A helper function to find out if a list of dicts contains values or
    not. The following values are considered as empty values:

    * ``[{"key": ""}]``
    * ``[{"key": None}]``
    * ``[{"key": []}]``

    Args:
        ``list_`` (list): A list of dicts.

    Returns:
        ``bool``. ``True`` if the list contains only empty dicts,
        ``False`` if not.
    """
    for d in list_:
        for key, value in d.items():
            if isinstance(value, dict):
                for k, v in value.items():
                    if v is not None and v != '':
                        return False
            elif value is not None and value != '' and value != []:
                return False
    return True


def get_session_questionnaire(configuration_code):
    """
    Return the data for a questionnaire from the session. The
    questionnaire(s) are stored in the session dictionary under the key
    ``session_questionnaires``.

    .. todo::
        Currently, only one questionnaire per configuration_code is
        stored to the session. In the fututre, it should be possible to
        store (and retrieve) multiple questionnaires.

    Args:
        ``configuration_code`` (str): The code of the configuration of
        the questionnaire to retrieve.

    Returns:
        ``dict``. The data dictionary of the questionnaire as found in
        the session or an empty dictionary (``{}``) if not found. Only
        the dictionary data is retrieved without additional data such as
        configuration_code or date of modification
    """
    session_questionnaires = session_store.get('session_questionnaires')
    if (isinstance(session_questionnaires, list)
            and len(session_questionnaires) > 0):

        for q in session_questionnaires:
            if q.get('configuration') == configuration_code:
                return q.get('questionnaire', {})

    return {}


def save_session_questionnaire(questionnaire, configuration_code):
    """
    Save the data of a questionnaire to the session, using the key
    ``session_questionnaires``.

    The questionnaires are stored in the session
    (``session['session_questionnaires']``) in the following format::

        [
            {
                "configuration": "CONFIGURATION_CODE",
                "modified": "DATETIME_OF_LAST_MODIFICATION",
                "questionnaire": {}  # data of the questionnaire
            }
        ]

    .. todo::
        Currently, only one questionnaire per configuration_code is
        stored to the session. In the fututre, it should be possible to
        store (and retrieve) multiple questionnaires.

    Args:
        ``session_questionnaire`` (dict): The data dictionary of the
        questionnaire to be stored.

        ``configuration_code`` (str): The code of the configuration of
        the questionnaire to store.
    """
    session_questionnaires = session_store.get('session_questionnaires', [])

    session_questionnaire = next((q for q in session_questionnaires if q.get(
        'configuration') == configuration_code), None)

    if session_questionnaire is None:
        # The questionnaire is not yet in the session
        session_questionnaire = {'configuration': configuration_code}
        session_questionnaires.append(session_questionnaire)

    # Update the session data
    session_questionnaire.update({
        'questionnaire': questionnaire,
        'modified': str(datetime.now()),
    })

    session_store['session_questionnaires'] = session_questionnaires
    session_store.save()


def clear_session_questionnaire(configuration_code=None):
    """
    Clear the data of a questionnaire from the session key
    ``session_questionnaires``.

    .. todo::
        Currently, only one questionnaire per configuration_code is
        stored to the session. In the fututre, it should be possible to
        store (and delete) multiple questionnaires.

    Kwargs:
        ``configuration_code`` (str): The code of the configuration of
        the questionnaire to clear. If not provided, all the session
        questionnaires will be cleared!
    """
    if configuration_code is None:
        session_store['session_questionnaires'] = []
    else:
        session_questionnaires = session_store.get(
            'session_questionnaires', [])
        for q in session_questionnaires:
            if q.get('configuration') == configuration_code:
                session_questionnaires.remove(q)
    session_store.save()

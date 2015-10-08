import urllib
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


def get_session_questionnaire(configuration_code, questionnaire_code, user):
    """
    Return the data for a questionnaire from the session. The
    questionnaire(s) are stored in the session dictionary under the key
    ``session_questionnaires``.

    .. seealso::
        :func:`save_session_questionnaire` for the format of session
        data.

    Args:
        ``configuration_code`` (str): The code of the configuration of
        the questionnaire to retrieve.

        ``questionnaire_code`` (str): The code of the questionnaire to
        retrieve. If ``questionnaire_code`` is ``None``, the code is set
        to ``new``.

    Returns:
        ``dict``. The dictionary of the session data if found (with
        ``questionnaire`` and ``links``) or an empty dictionary (``{}``)
        if not found.
    """
    session_questionnaires = session_store.get(
        user.id, {}).get('session_questionnaires')
    if not isinstance(session_questionnaires, dict):
        return {}

    if questionnaire_code is None:
        questionnaire_code = 'new'

    questionnaires = session_questionnaires.get(configuration_code, [])
    for q in questionnaires:
        if q.get('code') == questionnaire_code:
            return q

    return {}


def save_session_questionnaire(
        configuration_code, questionnaire_code, questionnaire_data,
        questionnaire_links, user):
    """
    Save the data of a questionnaire to the session, using the key
    ``session_questionnaires``.

    The questionnaires are stored in the session
    (``session['session_questionnaires']``) in the following format::

        {
            "CONFIGURATION_CODE": [
                {
                    "code": "QUESTIONNAIRE_CODE",  # if available, else "new"
                    "modified": "DATETIME_OF_LAST_MODIFICATION",
                    "questionnaire": {},  # data of the questionnaire
                    "links": {},  # data of the links
                }
            ]
        }

    Args:
        ``configuration_code`` (str): The code of the configuration of
        the questionnaire to store.

        ``questionnaire_code`` (str): The code of the questionnaire to
        store. If ``questionnaire_code`` is ``None``, the code is set to
        ``new``.

        ``session_questionnaire`` (dict): The data dictionary of the
        questionnaire to be stored.

        ``questionnaire_links`` (dict): The dictionary containing the
        links of the questionnaire. The format of the dictionary
        corresponds to the format used by the link forms to populate
        its fields.
    """
    if questionnaire_code is None:
        questionnaire_code = 'new'

    session_questionnaires = session_store.get(user.id, {}).get(
        'session_questionnaires', {}).get(configuration_code, [])

    session_questionnaire = next((q for q in session_questionnaires if q.get(
        'code') == questionnaire_code), None)

    if session_questionnaire is None:
        # The questionnaire is not yet in the session
        session_questionnaire = {'code': questionnaire_code}
        session_questionnaires.append(session_questionnaire)

    # Update the session data
    session_questionnaire.update({
        'questionnaire': questionnaire_data,
        'links': questionnaire_links,
        'modified': str(datetime.now()),
    })

    if user.id not in session_store:
        session_store[user.id] = {'session_questionnaires': {}}

    session_store[user.id]['session_questionnaires'][
        configuration_code] = session_questionnaires
    session_store.save()


def clear_session_questionnaire(
        configuration_code=None, questionnaire_code=None, user=None):
    """
    Clear the data of a questionnaire from the session key
    ``session_questionnaires``.

    Kwargs:
        ``configuration_code`` (str): The code of the configuration of
        the questionnaire to clear. If not provided, all the session
        questionnaires will be cleared!

        ``questionnaire_code`` (str): The code of the questionnaire to
        clear. If not provided, all the session questionnaires with the
        provided ``configuration_code`` will be cleared! If you want to
        clear all new questionnaires (without a code), you need to pass
        ``questionnaire_code=new`` explicitely.
    """
    if user.id not in session_store:
        return
    if configuration_code is None:
        session_store[user.id]['session_questionnaires'] = {}
    else:
        session_questionnaires = session_store.get(user.id, {}).get(
            'session_questionnaires', {})
        if questionnaire_code is None:
            if configuration_code in session_questionnaires:
                del(session_questionnaires[configuration_code])
        else:
            q_list = session_questionnaires.get(configuration_code, [])
            for q in q_list:
                if q.get('code') == questionnaire_code:
                    q_list.remove(q)
            session_questionnaires[configuration_code] = q_list
    session_store.save()


def url_with_querystring(path, **kwargs):
    """
    Build a URL with query strings.

    Args:
        ``path`` (str): The base path of the URL before the query
        strings.

    Kwargs:
        ``**(key=value)``: One or more parameters as keys and values to
        be added as query strings.

    Returns:
        ``str``. A URL with query strings.
    """
    return path + '?' + urllib.parse.urlencode(kwargs)

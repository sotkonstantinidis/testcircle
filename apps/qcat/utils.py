import urllib
import time
import logging


logger = logging.getLogger(__name__)


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


def time_cache_read(method):
    """
    Log spent time for configuration reading to file.
    This is slightly problematic, as sections are always cached so the comparison is unfair. We are
    mainly interested if there are 'spikes' are huge delays for the method get_configuration_by_code.
    """
    def timed(*args, **kwargs):
        ts = time.time()
        result = method(*args, **kwargs)
        te = time.time()
        logger.info(
            msg=';%2.2f ms;%s;%s' % (
                (te - ts) * 1000, method.__name__, kwargs.get('configuration_code')
            )
        )
        return result

    return timed

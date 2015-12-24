from django.conf import settings
from django.core.cache import cache
from django.utils.translation import to_locale, get_language


def get_configuration(configuration_code):
    """
    Return a QuestionnaireConfiguration. If cache is being used (setting
    ``USE_CACHING=True``), it is returned from the cache if found. If
    not found, it is added to the cache and returned. If the use of
    cache is deactivated, always a new configuration is returned.

    Args:
        ``configuration_code`` (str): The code of the configuration

    Returns:
        ``QuestionnaireConfiguration``. The Questionnaire configuration,
        either returned from cache or newly created.
    """
    from .configuration import QuestionnaireConfiguration
    try:
        use_caching = settings.USE_CACHING is True
    except AttributeError:
        use_caching = False

    cache_key = get_cache_key(configuration_code)

    if use_caching is True:
        configuration = cache.get(cache_key)
        if configuration is not None:
            return configuration

    configuration = QuestionnaireConfiguration(configuration_code)

    if use_caching is True:
        cache.set(cache_key, configuration)

    return configuration


def delete_configuration_cache(configuration_object):
    """
    Delete a configuration object from the cache if it exists.

    Args:
        ``configuration_object`` (``QuestionnaireConfiguration``): The
        configuration object whose configuration is to be deleted.
    """
    try:
        use_caching = settings.USE_CACHING is True
    except AttributeError:
        use_caching = False

    cache_key = get_cache_key(configuration_object.code)

    if use_caching is True:
        cache.delete_many([cache_key])


def get_cache_key(configuration_code):
    """
    Return the key under which a given configuration is stored in the
    cache. Currently, the key is composed as:
    ``[configuration_code]_[locale]``, for example ``technologies_en``.

    Args:
        ``configuration_code`` (str): The code of the configuration

    Returns:
        ``str``. The key for the cache.
    """
    return '{}_{}'.format(configuration_code, to_locale(get_language()))

from django.conf import settings
from django.core.cache import cache

from .configuration import QuestionnaireConfiguration


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
    try:
        use_caching = settings.USE_CACHING is True
    except AttributeError:
        use_caching = False

    if use_caching is True:
        configuration = cache.get(configuration_code)
        if configuration is not None:
            return configuration

    configuration = QuestionnaireConfiguration(configuration_code)

    if use_caching is True:
        cache.set(configuration_code, configuration)

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

    if use_caching is True:
        cache.delete_many([configuration_object.code])

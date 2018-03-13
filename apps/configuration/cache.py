from functools import lru_cache

from django.conf import settings
from django.core.cache import cache
from django.utils.translation import get_language, activate

from qcat.decorators import log_memory_usage


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

    if settings.USE_CACHING:
        cache_key = get_cache_key(configuration_code)
        configuration = get_cached_configuration(
            cache_key=cache_key,
            configuration_code=configuration_code
        )
        return configuration

    return get_configuration_by_code(configuration_code=configuration_code)


@lru_cache(maxsize=32)
@log_memory_usage
def get_cached_configuration(cache_key, configuration_code):
    """
    Simple retrieval. If object is not in the lru_cache, use the default cache
    from django as fallback.

    @todo: refactor configurations. this is a workaround due to bad performance
    which caches the configs in two places (memcached and python-threads -->
    twice the memory usage!). configurations should probably be cached by
    section or such.
    """
    configuration = cache.get(cache_key)

    if not configuration:
        configuration = get_configuration_by_code(configuration_code)
        cache.set(key=cache_key, value=configuration)

    return configuration


def get_configuration_by_code(configuration_code):
    """
    Get the configuration object.
    """
    from configuration.configuration import QuestionnaireConfiguration
    return QuestionnaireConfiguration(configuration_code)


def delete_configuration_cache(configuration_object):
    """
    Delete a configuration object from the cache (incl. lru_cache) if it exists. Also remove all
    QuestionnaireSections from the cache.
    cache.clear() is not used, as the cache is shared on some hosts.

    Args:
        ``configuration_object`` (``QuestionnaireConfiguration``): The
        configuration object whose configuration is to be deleted.
    """
    delete_section_caches(configuration_code=configuration_object.code)

    if settings.USE_CACHING:
        cache_key = get_cache_key(configuration_object.code)
        cache.delete(cache_key)
        get_cached_configuration.cache_clear()


def delete_section_caches(configuration_code: str):
    """
    Delete all cached sections for a configuration.
    """
    current_language = get_language()
    config = get_configuration(configuration_code=configuration_code)
    for language in settings.LANGUAGES:
        activate(language[0])
        for section in config.sections:
            cache_key = config.get_section_cache_key(section.keyword)
            cache.delete(cache_key)

    activate(current_language)


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
    return '{}_{}'.format(configuration_code, get_language())

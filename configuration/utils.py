from django.db.models import Q
from configuration.configuration import (
    QuestionnaireConfiguration,
)


def get_configuration_query_filter(configuration, only_current=False):
    """
    Return a Django ``Q`` object used to encapsulate SQL expressions.
    This object can be used to filter Questionnaires based on their
    configuration code.

    .. seealso::
        https://docs.djangoproject.com/en/1.7/topics/db/queries/#complex-lookups-with-q-objects

    The following rules apply:

    * By default, only questionnaires of the provided configuration are
      visible.

    * For ``wocat``, additionally configuration ``unccd`` is visible (
      combined through an ``OR`` statement)

    Args:
        ``configuration`` (str): The code of the (current)
        configuration.

    Kwargs:
        ``only_current`` (bool): If ``True``, always only the current
        configuration is returned as filter. Defaults to ``False``.

    Returns:
        ``django.db.models.Q``. A filter object.
    """
    if only_current is True:
        return Q(configurations__code=configuration)

    if configuration == 'wocat':
        return (
            Q(configurations__code='technologies') |
            Q(configurations__code='approaches') |
            Q(configurations__code='unccd'))

    return Q(configurations__code=configuration)


def get_configuration_index_filter(configuration, only_current=False):
    """
    Return the name of the index / indices to be searched by
    Elasticsearch based on their configuration code.

    The following rules apply:

    * By default, only questionnaires of the provided configuration
      are visible.

    * For ``wocat``, additionally configuration ``unccd`` is visible.

    Args:
        ``configuration`` (str): The code of the (current)
        configuration.

    Kwargs:
        ``only_current`` (bool): If ``True``, always only the current
        configuration_code is returned. Defaults to ``False``.

    Returns:
        ``list``. A list of configuration codes (the index/indices) to
        be searched.
    """
    if only_current is True:
        return [configuration]

    if configuration == 'wocat':
        return ['unccd', 'technologies', 'approaches']

    return [configuration]


def get_or_create_configuration(code, configurations):
    """
    Check if a given QuestionnaireConfiguration already exists in the
    provided dictionary and return it along with the dictionary if
    found. If it does not yet exist, create a QuestionnaireConfiguration
    with the given code, add it to dictionary and return both of them.

    Args:
        ``code`` (str): The code of the QuestionnaireConfiguration.

        ``configurations`` (dict): A dictionary with existing
        QuestionnaireConfigurations with their code as keys.
    """
    configuration = configurations.get(code, QuestionnaireConfiguration(code))
    configurations[code] = configuration
    return configuration, configurations

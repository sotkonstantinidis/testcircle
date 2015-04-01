from django.db.models import Q


def get_configuration_query_filter(configuration):
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

    Returns:
        ``django.db.models.Q``. A filter object.
    """
    if configuration == 'wocat':
        return (
            Q(configurations__code='wocat') | Q(configurations__code='unccd'))

    return Q(configurations__code=configuration)

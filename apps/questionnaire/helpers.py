"""
Custom file to prevent circular import on both models and serializers
"""
from .conf import settings


def key_properties(instance):
    """
    Serializer and model for questionnaires must provide all keys as property.
    As some keys ('configurations') shadow the actual model attribute, this
    checks for 'instance.<key>_property' on the instance before accessing
    'instance.key'.

    Args:
        instance: obj

    Returns:
        iterator

    """
    for key in settings.QUESTIONNAIRE_METADATA_KEYS:
        yield key, getattr(
            instance, '{}_property'.format(key), getattr(instance, key)
        )

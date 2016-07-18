import random
import string

from django.apps import apps
from django.db.models import Q
from configuration.cache import get_configuration
from questionnaire.models import Questionnaire


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

    * Use ``all`` to not filter Questionnaires by configurations at all.

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

    if configuration == 'all':
        return Q()

    if configuration == 'wocat':
        return (
            Q(configurations__code='technologies') |
            Q(configurations__code='approaches') |
            Q(configurations__code='unccd'))

    return Q(configurations__code=configuration)


def get_configuration_index_filter(
        configuration, only_current=False, query_param_filter=()):
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

        ``query_param_filter`` (tuple): If provided, takes precedence over the
        default rules.

    Returns:
        ``list``. A list of configuration codes (the index/indices) to
        be searched.
    """
    if query_param_filter:
        configurations = []
        for q in query_param_filter:
            if q == 'all':
                configurations.extend(['unccd', 'technologies', 'approaches'])
            else:
                configurations.append(q)
        return list(set(configurations))

    if only_current is True:
        return [configuration]

    if configuration == 'wocat':
        return ['unccd', 'technologies', 'approaches']

    return [configuration]


class ConfigurationList(object):
    """
    Helper object to keep track of QuestionnaireConfiguration objects.
    Check if a given configuration already exists and returns it if so.
    If not, it is created and added to the internal list. This prevents
    having to create a new configuration every time when looping objects
    of mixed configurations.
    """
    def __init__(self):
        self.configurations = {}

    def get(self, code):
        configuration = self.configurations.get(code)
        if configuration is None:
            configuration = get_configuration(code)
            self.configurations[code] = configuration
        return configuration


def create_new_code(configuration, questionnaire_data):
    """
    Create a new and non-existent code for a Questionnaire based on the
    configuration.

    TODO: This function is currently very limited, needs improvement.

    Args:
        ``configuration`` (str): The code of the configuration.

        ``questionnaire_data`` (dict): The data dictionary of the
        Questionnaire object.

    Returns:
        ``str``. A new and non-existent code.
    """
    def random_code(configuration):
        """
        Recursive helper function to create a random non-existent code.
        """
        code = '{}_{}'.format(
            configuration, ''.join(random.SystemRandom().choice(
                string.ascii_uppercase + string.digits) for _ in range(3)))
        if Questionnaire.objects.filter(code=code).count() != 0:
            return random_code(configuration)
        return code
    code = '{}_{}'.format(configuration, Questionnaire.objects.count())
    if Questionnaire.objects.filter(code=code).count() != 0:
        code = random_code(configuration)
    return code


def get_choices_from_model(model_name, only_active=True):
    """
    Return the values of a model as choices to be used in the form.

    Args:
        model_name: (str) The name of the model inside the ``configuration`` app
        only_active: (bool) If True, a filter is set to return only instances of
          the model with "active" = True

    Returns:
        list. A list of tuples where
            [0] The ID of the model instance
            [1] The string representation of the instance
    """
    choices = []
    try:
        model = apps.get_model(
            app_label='configuration', model_name=model_name)
        if only_active is True:
            objects = model.objects.filter(active=True).all()
        else:
            objects = model.objects.all()
        for o in objects:
            choices.append((o.id, str(o)))
    except LookupError:
        pass
    return choices

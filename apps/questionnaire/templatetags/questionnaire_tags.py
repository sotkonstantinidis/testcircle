from django import template
from questionnaire.models import Questionnaire

register = template.Library()


@register.simple_tag
def editable_css_class(questionnaire, user):
    """

    Args:
        questionnaire: questionnaire.models.Questionnaire
        user: accounts.models.User

    Returns:
        string: 'readonly' if questionnaire can't be edited by given user.

    """
    if isinstance(questionnaire, Questionnaire):
        return questionnaire.edit_css_class(user)
    return ''

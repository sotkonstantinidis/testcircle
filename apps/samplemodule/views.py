from django.contrib.auth.decorators import login_required

from accounts.decorators import force_login_check
from questionnaire.views import generic_questionnaire_details, \
    generic_questionnaire_view_step


@login_required
@force_login_check
def questionnaire_view_step(request, identifier, step):
    """
    View rendering the form of a single step of a new SAMPLEMODULE
    questionnaire in read-only mode.
    """
    return generic_questionnaire_view_step(
        request, identifier, step, 'samplemodule',
        page_title='SAMPLEMODULE')


def questionnaire_details(request, identifier):
    """
    View to show the details of an existing Approaches questionnaire.

    .. seealso::
        The actual rendering of the details is handled by the generic
        questionnaire function
        :func:`questionnaire.views.questionnaire_details`

    Args:
        ``request`` (django.http.HttpResponse): The request object.

        ``identifier`` (str): The identifier of the Questionnaire
        object.

    Returns:
        ``HttpResponse``. A rendered Http Response.
    """
    return generic_questionnaire_details(
        request, identifier, 'samplemodule', 'samplemodule')

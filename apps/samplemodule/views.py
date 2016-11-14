from questionnaire.views import generic_questionnaire_details


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

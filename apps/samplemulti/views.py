from django.contrib.auth.decorators import login_required

from questionnaire.views import generic_questionnaire_view_step


@login_required
def questionnaire_view_step(request, identifier, step):
    """
    View rendering the form of a single step of a new SAMPLEMULTI
    questionnaire in read-only mode.
    """
    return generic_questionnaire_view_step(
        request, identifier, step, 'samplemulti',
        page_title='SAMPLEMULTI')

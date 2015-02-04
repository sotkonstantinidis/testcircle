from django.contrib import messages
from django.http import Http404
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.utils.translation import ugettext as _

from configuration.configuration import QuestionnaireConfiguration
from qcat.utils import (
    clear_session_questionnaire,
    get_session_questionnaire,
    save_session_questionnaire,
)
from questionnaire.models import Questionnaire
from questionnaire.utils import is_empty_questionnaire


def generic_questionnaire_new_step(
        request, step, configuration_code, template, success_route):
    """
    A generic view to show the form of a single step of a new or edited
    questionnaire.

    By default, the form is shown. If the form was submitted, it is
    validated and if valid stored in the session, followed by a redirect
    to the desired route (``success_route``).

    Args:
        ``request`` (django.http.HttpRequest): The request object.

        ``step`` (str): The code of the questionnaire category.

        ``configuration_code`` (str): The code of the questionnaire
        configuration.

        ``template`` (str): The path of the template to be rendered for
        the form.

        ``success_route`` (str): The name of the route to be used to
        redirect to after successful form submission.

    Returns:
        ``HttpResponse``. A rendered Http Response.
    """
    questionnaire_configuration = QuestionnaireConfiguration(
        configuration_code)
    category = questionnaire_configuration.get_category(step)

    if category is None:
        raise Http404

    session_questionnaire = {}
    if request.method != 'POST':
        session_questionnaire = get_session_questionnaire()

    category_config, category_formsets = category.get_form(
        request.POST or None, initial_data=session_questionnaire)

    if request.method == 'POST':
        valid = True
        data = {}
        for __, subcategory_formsets in category_formsets:
            for formset in subcategory_formsets:

                valid = valid and formset.is_valid()

                if valid is False:
                    break

                for f in formset.forms:
                    questiongroup_keyword = f.prefix.split('-')[0]
                    try:
                        data[questiongroup_keyword].append(f.cleaned_data)
                    except KeyError:
                        data[questiongroup_keyword] = [f.cleaned_data]

        if valid is True:
            session_questionnaire = get_session_questionnaire()
            session_questionnaire.update(data)
            save_session_questionnaire(session_questionnaire)

            messages.success(
                request, _('[TODO] Data successfully stored to Session.'),
                fail_silently=True)
            return redirect(success_route)

    return render(request, template, {
        'category_formsets': category_formsets,
        'category_config': category_config
    })


def generic_questionnaire_new(
        request, configuration_code, template, success_route):
    """
    A generic view to show an entire questionnaire.

    By default, the overview of the questionnaire is shown. If the form
    was submitted, it is validated and if valid stored in the database,
    followed by a redirect to the desired route (``success_route``).

    Args:
        ``request`` (django.http.HttpRequest): The request object.

        ``configuration_code`` (str): The code of the questionnaire
        configuration.

        ``template`` (str): The path of the template to be rendered for
        the form.

        ``success_route`` (str): The name of the route to be used to
        redirect to after successful form submission.

    Returns:
        ``HttpResponse``. A rendered Http Response.
    """
    questionnaire_configuration = QuestionnaireConfiguration(
        configuration_code)
    session_questionnaire = get_session_questionnaire()

    if request.method == 'POST':
        if is_empty_questionnaire(session_questionnaire):
            messages.info(
                request, _('[TODO] You cannot submit an empty questionnaire'),
                fail_silently=True)
            return redirect(request.path)
        else:
            questionnaire = Questionnaire.create_new(session_questionnaire)
            clear_session_questionnaire()
            messages.success(
                request,
                _('[TODO] The questionnaire was successfully created.'),
                fail_silently=True)
            return redirect(success_route, questionnaire.id)

    categories = questionnaire_configuration.get_details(
        session_questionnaire, editable=True)

    return render(request, template, {
        'categories': categories
    })


def generic_questionnaire_details(
        request, questionnaire_id, configuration_code, template):
    """

    """
    questionnaire_object = get_object_or_404(
        Questionnaire, pk=questionnaire_id)
    questionnaire_configuration = QuestionnaireConfiguration(
        configuration_code)
    categories = questionnaire_configuration.get_details(
        questionnaire_object.data)

    return render(request, template, {
        'categories': categories,
        'questionnaire_id': questionnaire_id,
    })

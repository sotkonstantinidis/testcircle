from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_POST

from django.http import (
    Http404,
    JsonResponse,
)
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.utils.translation import ugettext as _, get_language

from configuration.configuration import QuestionnaireConfiguration
from qcat.utils import (
    clear_session_questionnaire,
    get_session_questionnaire,
    save_session_questionnaire,
)
from questionnaire.models import Questionnaire
from questionnaire.upload import handle_upload
from questionnaire.utils import (
    clean_questionnaire_data,
    get_questiongroup_data_from_translation_form,
    get_questionnaire_data_in_single_language,
    get_questionnaire_data_for_translation_form,
)


@login_required
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

    # TODO: Make this more dynamic
    original_locale = None
    current_locale = get_language()
    show_translation = (
        original_locale is not None and current_locale != original_locale)

    initial_data = get_questionnaire_data_for_translation_form(
        session_questionnaire, current_locale, original_locale)

    category_config, category_formsets = category.get_form(
        post_data=request.POST or None, initial_data=initial_data,
        show_translation=show_translation)

    if request.method == 'POST':
        valid = True
        data = {}
        for __, subcategory_formsets in category_formsets:
            for __, questiongroup_formset in subcategory_formsets:

                valid = valid and questiongroup_formset.is_valid()

                if valid is False:
                    break

                for f in questiongroup_formset.forms:
                    questiongroup_keyword = f.prefix.split('-')[0]
                    cleaned_data = \
                        get_questiongroup_data_from_translation_form(
                            f.cleaned_data, current_locale, original_locale)
                    try:
                        data[questiongroup_keyword].append(cleaned_data)
                    except KeyError:
                        data[questiongroup_keyword] = [cleaned_data]

        if valid is True:
            session_questionnaire = get_session_questionnaire()
            session_questionnaire.update(data)

            cleaned_questionnaire_data, errors = clean_questionnaire_data(
                session_questionnaire, questionnaire_configuration)
            if errors:
                messages.error(
                    request, 'Something went wrong. The step cannot be saved '
                    'because of the following errors: <br/>{}'.format(
                        '<br/>'.join(errors)))

            save_session_questionnaire(cleaned_questionnaire_data)

            messages.success(
                request, _('[TODO] Data successfully stored to Session.'),
                fail_silently=True)
            return redirect(success_route)

    return render(request, template, {
        'category_formsets': category_formsets,
        'category_config': category_config
    })


@login_required
def generic_questionnaire_new(
        request, configuration_code, template, success_route, edit_step_route,
        questionnaire_id=None):
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

        ``questionnaire_id`` (id): The ID of a questionnaire if the it
        is an edit form.

    Returns:
        ``HttpResponse``. A rendered Http Response.
    """
    questionnaire_configuration = QuestionnaireConfiguration(
        configuration_code)

    if questionnaire_id is not None:
        questionnaire_object = get_object_or_404(
            Questionnaire, pk=questionnaire_id)
        save_session_questionnaire(questionnaire_object.data)

    session_questionnaire = get_session_questionnaire()

    if request.method == 'POST':
        cleaned_questionnaire_data, errors = clean_questionnaire_data(
            session_questionnaire, questionnaire_configuration)
        if errors:
            messages.error(
                request, 'Something went wrong. The questionnaire cannot be '
                'submitted because of the following errors: <br/>{}'.format(
                    '<br/>'.join(errors)))
        if not cleaned_questionnaire_data:
            messages.info(
                request, _('[TODO] You cannot submit an empty questionnaire'),
                fail_silently=True)
            return redirect(request.path)
        else:
            questionnaire = Questionnaire.create_new(
                configuration_code, session_questionnaire)
            clear_session_questionnaire()
            messages.success(
                request,
                _('[TODO] The questionnaire was successfully created.'),
                fail_silently=True)
            return redirect(success_route, questionnaire.id)

    data = get_questionnaire_data_in_single_language(
        session_questionnaire, get_language())

    categories = questionnaire_configuration.get_details(
        data, editable=True, edit_step_route=edit_step_route)
    category_names = []
    for category in questionnaire_configuration.categories:
        category_names.append((category.keyword, category.label))

    return render(request, template, {
        'categories': categories,
        'category_names': tuple(category_names),
        'questionnaire_id': questionnaire_id,
    })


def generic_questionnaire_details(
        request, questionnaire_id, configuration_code, template):
    """
    A generic view to show the details of a questionnaire.

    Args:
        ``request`` (django.http.HttpRequest): The request object.

        ``questionnaire_id`` (int): The ID of the questionnaire to
        display.

        ``configuration_code`` (str): The code of the questionnaire
        configuration.

        ``template`` (str): The path of the template to be rendered for
        the details.

    Returns:
        ``HttpResponse``. A rendered Http Response.
    """
    questionnaire_object = get_object_or_404(
        Questionnaire, pk=questionnaire_id)
    questionnaire_configuration = QuestionnaireConfiguration(
        configuration_code)
    data = get_questionnaire_data_in_single_language(
        questionnaire_object.data, get_language())
    categories = questionnaire_configuration.get_details(data)

    return render(request, template, {
        'categories': categories,
        'questionnaire_id': questionnaire_id,
    })


def generic_questionnaire_list(
        request, configuration_code, template, details_route):
    """
    A generic view to show a list of questionnaires.

    Args:
        ``request`` (django.http.HttpRequest): The request object.

        ``configuration_code`` (str): The code of the questionnaire
        configuration.

        ``template`` (str): The path of the template to be rendered for
        the list.

        ``details_route`` (str): The route name of the details page of
        each questionnaire.

    Returns:
        ``HttpResponse``. A rendered Http Response.
    """
    questionnaires = list(Questionnaire.objects.filter(
        configurations__code=configuration_code))
    questionnaire_configuration = QuestionnaireConfiguration(
        configuration_code)
    list_data = questionnaire_configuration.get_list_data(
        questionnaires, details_route, get_language())

    return render(request, template, {
        'list_header': list_data[0],
        'list_data': list_data[1:],
    })


@login_required
@require_POST
def generic_file_upload(request):
    """
    A view to handle file uploads. Can only be called with POST requests
    and returns a JSON.

    Args:
        ``request`` (django.http.HttpRequest): The request object. Only
        request method ``POST`` is accepted and the following parameters
        are valid:

            ``request.FILES`` (mandatory): The uploaded file.

            ``request.POST.preview_format`` (optional): If available,
            the URL for this format will be returned. If not specified,
            the URL to the original file will be returned.

    Returns:
        ``JsonResponse``. A JSON containing the following entries::

          # Successful requests
          {
            "success": true,
            "uid": "UID",          # The UID of the generated file
            "url": "URL"           # The URL of the preview file generated
                                   # (see request.POST.preview_format)
          }

          # Error requests (status_code: 400)
          {
            "success": false,
            "msg": "ERROR MESSAGE"
          }
    """
    ret = {
        'success': False,
    }

    files = request.FILES.getlist('file')
    if len(files) != 1:
        ret['msg'] = _('No or multiple files provided.')
        return JsonResponse(ret, status=400)
    file = files[0]

    try:
        db_file = handle_upload(file)
    except Exception as e:
        ret['msg'] = str(e)
        return JsonResponse(ret, status=400)

    ret = {
        'success': True,
        'uid': str(db_file.uuid),
        'url': db_file.get_url(thumbnail=request.POST.get('preview_format')),
    }
    return JsonResponse(ret)

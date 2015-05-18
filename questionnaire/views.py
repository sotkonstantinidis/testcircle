from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.views.decorators.http import require_POST

from django.http import (
    Http404,
    HttpResponse,
    JsonResponse,
)
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.utils.translation import ugettext as _, get_language

from configuration.configuration import QuestionnaireConfiguration
from configuration.utils import get_configuration_query_filter
from qcat.utils import (
    clear_session_questionnaire,
    get_session_questionnaire,
    save_session_questionnaire,
)
from questionnaire.models import (
    Questionnaire,
    File,
)
from questionnaire.upload import (
    handle_upload,
    retrieve_file,
)
from questionnaire.utils import (
    clean_questionnaire_data,
    get_active_filters,
    get_questiongroup_data_from_translation_form,
    get_questionnaire_data_in_single_language,
    get_questionnaire_data_for_translation_form,
)


@login_required
def generic_questionnaire_new_step(
        request, step, configuration_code, url_namespace,
        page_title='QCAT Form'):
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

        ``url_namespace`` (str): The namespace of the questionnaire
        URLs. It is assumed that all questionnaire apps have the same
        routes for their questionnaires
        (e.g. ``wocat:questionnaire_new``)

    Kwargs:
        ``page_title`` (str): The page title to be used in the HTML
        template. Defaults to ``QCAT Form``.

    Returns:
        ``HttpResponse``. A rendered Http Response.
    """
    def _validate_formsets(
            nested_formsets, current_locale, original_locale):
        """
        Helper function to validate a set of nested formsets. Unnests
        the formsets and validates each of them. Returns the cleaned
        data if the formsets are valid.

        Args:
            ``nested_formsets`` (list): A nested list of tuples with
            formsets. Each tuple contains of the configuration [0] and
            the formsets [1]

            ``current_locale`` (str): The current locale.

            ``original_locale`` (str): The original locale in which the
            questionnaire was originally created.

        Returns:
            ``dict``. The cleaned data dictionary if the formsets are
            valid. Else ``None``.

            ``bool``. A boolean indicating whether the formsets are
            valid or not.
        """
        def unnest_formets(nested_formsets):
            """
            Small helper function to unnest nested formsets. Returns them
            all in a flat array.
            """
            ret = []
            for __, f in nested_formsets:
                if isinstance(f, list):
                    ret.extend(unnest_formets(f))
                else:
                    ret.append(f)
            return ret

        data = {}
        is_valid = True
        formsets = unnest_formets(nested_formsets)
        for formset in formsets:
            is_valid = is_valid and formset.is_valid()

            if is_valid is False:
                return None, False

            for f in formset.forms:
                questiongroup_keyword = f.prefix.split('-')[0]
                cleaned_data = \
                    get_questiongroup_data_from_translation_form(
                        f.cleaned_data, current_locale, original_locale)
                try:
                    data[questiongroup_keyword].append(cleaned_data)
                except KeyError:
                    data[questiongroup_keyword] = [cleaned_data]

        return data, True
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

    overview_url = '{}#{}'.format(
        reverse('{}:questionnaire_new'.format(url_namespace)), step)

    valid = True
    if request.method == 'POST':

        data, valid = _validate_formsets(
            category_formsets, current_locale, original_locale)

        if valid is True:
            session_questionnaire = get_session_questionnaire()
            session_questionnaire.update(data)

            cleaned_questionnaire_data, errors = clean_questionnaire_data(
                session_questionnaire, questionnaire_configuration)
            if errors:
                valid = False
                messages.error(
                    request, 'Something went wrong. The step cannot be saved '
                    'because of the following errors: <br/>{}'.format(
                        '<br/>'.join(errors)))
            else:
                save_session_questionnaire(cleaned_questionnaire_data)

                messages.success(
                    request, _('[TODO] Data successfully stored to Session.'),
                    fail_silently=True)
                return redirect(overview_url)

    return render(request, 'form/category.html', {
        'category_formsets': category_formsets,
        'category_config': category_config,
        'title': page_title,
        'overview_url': overview_url,
        'valid': valid,
        'configuration_name': url_namespace,
    })


@login_required
def generic_questionnaire_new(
        request, configuration_code, template, url_namespace,
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

        ``template`` (str): The name and path of the template to render
        the response with.

        ``url_namespace`` (str): The namespace of the questionnaire
        URLs. It is assumed that all questionnaire apps have the same
        routes for their questionnaires
        (e.g. ``wocat:questionnaire_new``)

    Kwargs:
        ``questionnaire_id`` (id): The ID of a questionnaire if the it
        is an edit form.

        ``page_title`` (str): The page title to be used in the HTML
        template. Defaults to ``QCAT Form``.

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
            return redirect(
                '{}:questionnaire_details'.format(url_namespace),
                questionnaire.id)

    data = get_questionnaire_data_in_single_language(
        session_questionnaire, get_language())

    sections = questionnaire_configuration.get_details(
        data, editable=True,
        edit_step_route='{}:questionnaire_new_step'.format(url_namespace))

    images = questionnaire_configuration.get_image_data(data)

    return render(request, template, {
        'images': images,
        'sections': sections,
        'questionnaire_id': questionnaire_id,
        'mode': 'edit',
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

        ``template`` (str): The name and path of the template to render
        the response with.

    Returns:
        ``HttpResponse``. A rendered Http Response.
    """
    questionnaire_object = get_object_or_404(
        Questionnaire, pk=questionnaire_id)
    questionnaire_configuration = QuestionnaireConfiguration(
        configuration_code)
    data = get_questionnaire_data_in_single_language(
        questionnaire_object.data, get_language())

    sections = questionnaire_configuration.get_details(
        data=data, questionnaire_object=questionnaire_object)

    images = questionnaire_configuration.get_image_data(data)

    return render(request, template, {
        'images': images,
        'sections': sections,
        'questionnaire_id': questionnaire_id,
        'mode': 'view',
    })


def generic_questionnaire_list(
        request, configuration_code, template=None, filter_url='', limit=10,
        only_current=False):
    """
    A generic view to show a list of questionnaires.

    Args:
        ``request`` (django.http.HttpRequest): The request object.

        ``configuration_code`` (str): The code of the questionnaire
        configuration.

    Kwargs:
        ``template`` (str): The path of the template to be rendered for
        the list.

        ``filter_url`` (str): The URL of the view used to render the
        list partially. Used by AJAX requests to update the list.

        ``limit`` (int): The limit of results the list will return.

        ``only_current`` (bool): A boolean indicating whether to include
        only questionnaires from the current configuration. Passed to
        :func:`configuration.utils.get_configuration_query_filter`

    Returns:
        ``HttpResponse``. A rendered Http Response.
    """
    questionnaire_configuration = QuestionnaireConfiguration(
        configuration_code)

    questionnaires = Questionnaire.objects.filter(
        get_configuration_query_filter(
            configuration_code, only_current=only_current))

    # Apply filters
    active_filters = get_active_filters(
        questionnaire_configuration, request.GET)
    # TODO: Improve the filtering, also performance wise.
    for active_filter in active_filters:
        filtered = []
        if active_filter['type'] in ['checkbox', 'image_checkbox']:
            for filtered_questionnaire in Questionnaire.objects.raw("""
                select *
                from questionnaire_questionnaire,
                lateral jsonb_array_elements(data -> %s) questiongroup
                where questiongroup->%s ? %s;
            """, [active_filter['questiongroup'], active_filter['key'],
                    active_filter['value']]):
                filtered.append(filtered_questionnaire)
        else:
            raise NotImplemented()

        questionnaires = questionnaires.filter(id__in=[q.id for q in filtered])

    # Apply limit
    questionnaires = questionnaires[:limit]

    # Get the values needed for the list template
    questionnaire_value_list = questionnaire_configuration.get_list_data(
        questionnaires)

    # Add the configuration of the filter
    filter_configuration = questionnaire_configuration.\
        get_filter_configuration()

    template_values = {
        'questionnaire_value_list': questionnaire_value_list,
        'filter_configuration': filter_configuration,
        'active_filters': active_filters,
        'filter_url': filter_url,
    }

    if template is None:
        return template_values

    return render(request, template, template_values)


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

    Returns:
        ``JsonResponse``. A JSON containing the following entries::

          # Successful requests
          {
            "success": true,
            "uid": "UID",          # The UID of the generated file
            "url": "URL"           # The URL of the uploaded file
            "interchange": "XYZ"   # The interchange value with all the
                                   # thumbnails.
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
        'interchange': db_file.get_interchange_urls(),
        'url': db_file.get_url(),
    }
    return JsonResponse(ret)


def generic_file_serve(request, action, uid):
    """
    A view to handle display or download of uploaded files. This
    function should only be used if you don't know the name of the
    thumbnail on the client side as this view has to read the file
    before serving it. On server side, if you want the URL for a
    thumbnail, use the function
    :func:`questionnaire.upload.get_url_by_identifier`.

    Args:
        ``request`` (django.http.HttpRequest): The request object.

        ``action`` (str): The action to perform with the file. Available
        options are ``display``, ``download`` and ``interchange``.

        ``uid`` (str): The UUID of the file object.

    GET Parameters:
        ``format`` (str): The name of the thumbnail format for images.

    Returns:
        ``HttpResponse``. A Http Response with the file if found, 404 if
        not found. If the ``action=interchange`` is set, a string with
        the interchange data is returned.
    """
    if action not in ['display', 'download', 'interchange']:
        raise Http404()

    file_object = get_object_or_404(File, uuid=uid)

    if action == 'interchange':
        return HttpResponse(file_object.get_interchange_urls())

    thumbnail = request.GET.get('format')
    try:
        file, filename = retrieve_file(file_object, thumbnail=thumbnail)
    except:
        raise Http404()
    content_type = file_object.content_type

    if thumbnail is not None:
        content_type = 'image/jpeg'

    response = HttpResponse(file, content_type=content_type)
    if action == 'download':
        response['Content-Disposition'] = 'attachment; filename={}'.format(
            filename)
        response['Content-Length'] = file_object.size

    return response

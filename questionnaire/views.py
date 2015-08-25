from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.urlresolvers import reverse
from django.http import (
    Http404,
    HttpResponse,
    JsonResponse,
)
from django.middleware.csrf import get_token
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.template.loader import render_to_string
from django.utils.translation import ugettext as _, get_language
from django.views.decorators.http import require_POST

from configuration.cache import get_configuration
from configuration.utils import (
    get_configuration_index_filter,
)
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
    get_link_data,
    get_list_values,
    get_questiongroup_data_from_translation_form,
    get_questionnaire_data_in_single_language,
    get_questionnaire_data_for_translation_form,
    handle_review_actions,
    query_questionnaires_for_link,
    query_questionnaire,
    query_questionnaires,
)
from questionnaire.view_utils import (
    ESPagination,
    get_page_parameter,
    get_pagination_parameters,
    get_paginator,
    get_limit_parameter,
)
from search.search import advanced_search


@login_required
def generic_questionnaire_link_form(
        request, configuration_code, url_namespace, page_title='QCAT Links',
        identifier=None):
    """
    A generic view to add or remove linked questionnaires. By default,
    the forms are shown. If the form was submitted, the submitted
    questionnaires are validated and stored in the session, followed by
    a redirect to the overview.

    Args:
        ``request`` (django.http.HttpRequest): The request object.

        ``configuration_code`` (str): The code of the questionnaire
        configuration.

        ``url_namespace`` (str): The namespace of the questionnaire
        URLs. It is assumed that all questionnaire apps have the same
        routes for their questionnaires
        (e.g. ``wocat:questionnaire_new``)

    Kwargs:
        ``page_title`` (str): The page title to be used in the HTML
        template. Defaults to ``QCAT Form``.

        ``identifier`` (str) The identifier of the Questionnaire if
        available.

    Returns:
        ``HttpResponse``. A rendered Http Response.
    """
    questionnaire_configuration = get_configuration(configuration_code)
    links_configuration = questionnaire_configuration.get_links_configuration()

    session_data = get_session_questionnaire(configuration_code, identifier)

    link_forms = []
    for links_config in links_configuration:
        config_code = links_config.get('keyword')
        initial_data = session_data.get('links', {}).get(config_code, [])
        link_forms.append(
            ({
                'search_url': reverse(
                    '{}:questionnaire_link_search'.format(config_code)),
                'keyword': config_code,
                'label': config_code,  # TODO
            }, initial_data))

    if identifier is None:
        overview_url = '{}#links'.format(
            reverse('{}:questionnaire_new'.format(url_namespace)))
    else:
        overview_url = '{}#links'.format(reverse(
            '{}:questionnaire_edit'.format(
                url_namespace), kwargs={'identifier': identifier}))

    valid = True
    if request.method == 'POST':

        link_data = {}
        for submitted_key in request.POST.keys():

            if not submitted_key.startswith('links__'):
                continue

            cleaned_links = []
            for submitted_link in request.POST.getlist(submitted_key):
                try:
                    link_object = Questionnaire.objects.get(pk=submitted_link)
                except Questionnaire.DoesNotExist:
                    messages.error(
                        request, 'The linked questionnaire with ID {} '
                        'does not exist'.format(submitted_link))
                    valid = False
                    continue

                link_configuration_code = submitted_key.replace('links__', '')
                current_link_data = get_link_data(
                    [link_object],
                    link_configuration_code=link_configuration_code)
                cleaned_links.extend(
                    current_link_data.get(link_configuration_code))
                if len(cleaned_links):
                    link_data[link_configuration_code] = cleaned_links

        if valid is True:
            save_session_questionnaire(
                configuration_code, identifier,
                session_data.get('questionnaire', {}), link_data)
            messages.success(
                request, _('Data successfully stored to Session.'))
            return redirect(overview_url)

    return render(request, 'form/links.html', {
        'valid': valid,
        'overview_url': overview_url,
        'link_forms': link_forms,
        'configuration_name': url_namespace,
        'title': page_title,
    })


def generic_questionnaire_link_search(request, configuration_code):
    """
    A generic view to return search for questionnaires to be used in the
    linked form. Returns the found Questionnaires in JSON format.

    The search happens in the database as users need to see their own
    pending changes.

    A generic view to add or remove linked questionnaires. By default,
    the forms are shown. If the form was submitted, the submitted
    questionnaires are validated and stored in the session, followed by
    a redirect to the overview.

    Args:
        ``request`` (django.http.HttpResponse): The request object. The
        search term is passed as GET parameter ``q`` of the request.

        ``configuration_code`` (str): The code of the questionnaire
        configuration.

    Returns:
        ``JsonResponse``. A rendered JSON Response. If successful, the
        response contains the following keys:

            ``total`` (int): An integer indicating the total amount of
            results found.

            ``data`` (list): A list of the results returned. This can
            contain fewer items than the total count indicates as there
            is a limit applied to the results.
    """
    q = request.GET.get('q', None)
    if q is None:
        return JsonResponse({})

    configuration = get_configuration(configuration_code)

    total, questionnaires = query_questionnaires_for_link(configuration, q)

    link_template = '{}/questionnaire/partial/link.html'.format(
        configuration_code)
    link_route = '{}:questionnaire_details'.format(configuration_code)

    link_data = configuration.get_list_data([d.data for d in questionnaires])
    data = []
    for i, d in enumerate(questionnaires):
        display = render_to_string(link_template, {
            'link_data': link_data[i],
            'link_route': link_route,
            'questionnaire_identifier': d.code,
        })

        name = configuration.get_questionnaire_name(d.data)
        try:
            original_lang = d.questionnairetranslation_set.first().language
        except AttributeError:
            original_lang = None

        data.append({
            'name': name.get(get_language(), name.get(original_lang, '')),
            'id': d.id,
            'value': d.id,
            'code': d.code,
            'display': display,
        })

    ret = {
        'total': total,
        'data': data,
    }
    return JsonResponse(ret)


@login_required
def generic_questionnaire_new_step(
        request, step, configuration_code, url_namespace,
        page_title='QCAT Form', identifier=None):
    """
    A generic view to show the form of a single step of a new or edited
    questionnaire.

    By default, the form is shown. If the form was submitted, it is
    validated and if valid stored in the session, followed by a redirect
    to the overview.

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

        ``identifier`` (str) The identifier of the Questionnaire if
        available.

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

    questionnaire_configuration = get_configuration(configuration_code)
    category = questionnaire_configuration.get_category(step)

    if category is None:
        raise Http404

    session_questionnaire = {}
    if request.method != 'POST':
        session_data = get_session_questionnaire(
            configuration_code, identifier)
        session_questionnaire = session_data.get('questionnaire', {})

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

    if identifier is None:
        overview_url = '{}#{}'.format(
            reverse('{}:questionnaire_new'.format(url_namespace)), step)
    else:
        overview_url = '{}#{}'.format(reverse('{}:questionnaire_edit'.format(
            url_namespace), kwargs={'identifier': identifier}), step)

    valid = True
    if request.method == 'POST':

        data, valid = _validate_formsets(
            category_formsets, current_locale, original_locale)

        if valid is True:
            session_data = get_session_questionnaire(
                configuration_code, identifier)
            session_questionnaire = session_data.get('questionnaire', {})
            session_questionnaire.update(data)

            questionnaire_data, errors = clean_questionnaire_data(
                session_questionnaire, questionnaire_configuration)
            if errors:
                valid = False
                messages.error(
                    request, 'Something went wrong. The step cannot be saved '
                    'because of the following errors: <br/>{}'.format(
                        '<br/>'.join(errors)), extra_tags='safe')
            else:
                save_session_questionnaire(
                    configuration_code, identifier, questionnaire_data,
                    session_data.get('links', {}))

                messages.success(
                    request, _('Data successfully stored to Session.'))
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
        request, configuration_code, template, url_namespace, identifier=None):
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
        ``identifier`` (str): The identifier of a questionnaire if it is
        an edit form.

        ``page_title`` (str): The page title to be used in the HTML
        template. Defaults to ``QCAT Form``.

    Returns:
        ``HttpResponse``. A rendered Http Response.
    """
    questionnaire_configuration = get_configuration(configuration_code)
    if identifier is not None:
        # For edits, copy the data to the session first (if it was
        # edited for the first time only).
        questionnaire_object = query_questionnaire(request, identifier).first()
        if questionnaire_object is None:
            raise Http404()
        session_data = get_session_questionnaire(
            configuration_code, identifier)
        if session_data.get('questionnaire') is None:
            questionnaire_links = get_link_data(
                questionnaire_object.links.all())
            save_session_questionnaire(
                configuration_code, identifier,
                questionnaire_data=questionnaire_object.data,
                questionnaire_links=questionnaire_links)
    else:
        questionnaire_object = None
        identifier = 'new'

    session_data = get_session_questionnaire(configuration_code, identifier)
    session_questionnaire = session_data.get('questionnaire', {})
    session_links = session_data.get('links', {})

    if request.method == 'POST':
        cleaned_questionnaire_data, errors = clean_questionnaire_data(
            session_questionnaire, questionnaire_configuration)
        if errors:
            messages.error(
                request, 'Something went wrong. The questionnaire cannot be '
                'submitted because of the following errors: <br/>{}'.format(
                    '<br/>'.join(errors)), extra_tags='safe')
        if not cleaned_questionnaire_data:
            messages.info(
                request, _('You cannot submit an empty questionnaire'),
                fail_silently=True)
            return redirect(request.path)
        else:
            questionnaire = Questionnaire.create_new(
                configuration_code, session_questionnaire, request.user,
                previous_version=questionnaire_object)
            clear_session_questionnaire(configuration_code=configuration_code)

            for __, linked_questionnaires in session_links.items():
                for linked in linked_questionnaires:
                    try:
                        link = Questionnaire.objects.get(pk=linked.get('id'))
                    except Questionnaire.DoesNotExist:
                        continue
                    questionnaire.add_link(link)

            messages.success(
                request,
                _('The questionnaire was successfully created.'),
                fail_silently=True)

            return redirect('{}#top'.format(
                reverse('{}:questionnaire_details'.format(
                    url_namespace), args=[questionnaire.code])))

    data = get_questionnaire_data_in_single_language(
        session_questionnaire, get_language())

    sections = questionnaire_configuration.get_details(
        data, editable=True,
        edit_step_route='{}:questionnaire_new_step'.format(url_namespace),
        questionnaire_object=questionnaire_object)

    images = questionnaire_configuration.get_image_data(data)

    link_ids = []
    for __, linked_questionnaires in session_links.items():
        link_ids.extend([l.get('id') for l in linked_questionnaires])

    links_by_configuration = {}
    for linked in Questionnaire.objects.filter(id__in=link_ids):
        configuration = linked.configurations.first()
        if configuration is None:
            continue
        if configuration.code not in links_by_configuration:
            links_by_configuration[configuration.code] = [linked]
        else:
            links_by_configuration[configuration.code].append(linked)

    link_display = {}
    for configuration, links in links_by_configuration.items():
        link_display[configuration] = get_list_values(
            configuration_code=configuration, questionnaire_objects=links,
            with_links=False)

    # Add the configuration of the filter
    filter_configuration = questionnaire_configuration.\
        get_filter_configuration()

    return render(request, template, {
        'images': images,
        'sections': sections,
        'questionnaire_identifier': identifier,
        'mode': 'edit',
        'links': link_display,
        'filter_configuration': filter_configuration,
    })


def generic_questionnaire_details(
        request, identifier, configuration_code, url_namespace, template):
    """
    A generic view to show the details of a questionnaire.

    Args:
        ``request`` (django.http.HttpRequest): The request object.

        ``identifier`` (str): The identifier of the questionnaire to
        display.

        ``configuration_code`` (str): The code of the questionnaire
        configuration.

        ``url_namespace`` (str): The namespace of the questionnaire
        URLs.

        ``template`` (str): The name and path of the template to render
        the response with.

    Returns:
        ``HttpResponse``. A rendered Http Response.
    """
    questionnaire_object = query_questionnaire(request, identifier).first()
    if questionnaire_object is None:
        raise Http404()
    questionnaire_configuration = get_configuration(configuration_code)
    data = get_questionnaire_data_in_single_language(
        questionnaire_object.data, get_language())

    if request.method == 'POST':
        handle_review_actions(
            request, questionnaire_object, configuration_code)
        return redirect(
            '{}:questionnaire_details'.format(url_namespace),
            questionnaire_object.code)

    # Show the review panel only if the user is logged in and if the
    # version to be shown is not active.
    obj_status = questionnaire_object.status
    if obj_status != 3:
        review_config = {
            'review_status': obj_status,
            'csrf_token_value': get_token(request),
        }
    else:
        review_config = {}

    # Collect additional values needed for the review process
    if obj_status == 2:
        # Pending: Can the version be reviewed?
        reviewable = questionnaire_object.status == 2 and \
            request.user.has_perm('questionnaire.can_moderate')
        review_config.update({
            'reviewable': reviewable,
        })

    sections = questionnaire_configuration.get_details(
        data=data, review_config=review_config,
        questionnaire_object=questionnaire_object)

    images = questionnaire_configuration.get_image_data(data)

    links_by_configuration = {}
    for linked in questionnaire_object.links.all():
        configuration = linked.configurations.first()
        if configuration is None:
            continue
        if configuration.code not in links_by_configuration:
            links_by_configuration[configuration.code] = [linked]
        else:
            links_by_configuration[configuration.code].append(linked)

    link_display = {}
    for configuration, links in links_by_configuration.items():
        link_display[configuration] = get_list_values(
            configuration_code=configuration, questionnaire_objects=links,
            with_links=False)

    # Add the configuration of the filter
    filter_configuration = questionnaire_configuration.\
        get_filter_configuration()

    return render(request, template, {
        'images': images,
        'sections': sections,
        'questionnaire_identifier': identifier,
        'mode': 'view',
        'links': link_display,
        'filter_configuration': filter_configuration,
    })


def generic_questionnaire_list(
        request, configuration_code, template=None, filter_url='', limit=None,
        only_current=False, db_query=False):
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
        :func:`questionnaire.utils.query_questionnaires`

        ``db_query`` (bool): A boolean indicating whether to query the
        database for results instead of using Elasticsearch. Please note
        that filters are ignored if querying the database.

    Returns:
        ``HttpResponse``. A rendered Http Response.
    """
    questionnaire_configuration = get_configuration(configuration_code)

    # Get the filters and prepare them to be passed to the search.
    active_filters = get_active_filters(
        questionnaire_configuration, request.GET)
    query_string = ''
    filter_params = []
    for active_filter in active_filters:
        filter_type = active_filter.get('type')
        if filter_type in ['_search']:
            query_string = active_filter.get('value', '')
        elif filter_type in [
                'checkbox', 'image_checkbox', '_date', 'select_type']:
            filter_params.append(
                (active_filter.get('questiongroup'),
                 active_filter.get('key'), active_filter.get('value'), None,
                 active_filter.get('type')))
        else:
            raise NotImplementedError(
                'Type "{}" is not valid for filters'.format(filter_type))

    if limit is None:
        limit = get_limit_parameter(request)
    page = get_page_parameter(request)
    offset = page * limit - limit

    if db_query is True:

        # Limit is handled by the paginator
        questionnaire_objects = query_questionnaires(
            request, configuration_code, only_current=only_current,
            limit=None)

        questionnaires, paginator = get_paginator(
            questionnaire_objects, page, limit)

        list_values = get_list_values(
            configuration_code=configuration_code,
            questionnaire_objects=questionnaires)

    else:
        search_configuration_codes = get_configuration_index_filter(
            configuration_code, only_current=only_current)

        search = advanced_search(
            filter_params=filter_params, query_string=query_string,
            configuration_codes=search_configuration_codes, limit=limit,
            offset=offset)

        es_hits = search.get('hits', {})
        es_pagination = ESPagination(
            es_hits.get('hits', []), es_hits.get('total', 0))

        questionnaires, paginator = get_paginator(es_pagination, page, limit)

        list_values = get_list_values(
            configuration_code=configuration_code, es_hits=questionnaires)

    # Add the configuration of the filter
    filter_configuration = questionnaire_configuration.\
        get_filter_configuration()

    template_values = {
        'list_values': list_values,
        'filter_configuration': filter_configuration,
        'active_filters': active_filters,
        'filter_url': filter_url,
    }

    # Add the pagination parameters
    pagination_params = get_pagination_parameters(
        request, paginator, questionnaires)
    template_values.update(pagination_params)

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

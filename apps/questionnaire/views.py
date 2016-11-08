import collections
import contextlib
import json
import logging
from itertools import chain
from os.path import isfile, join

from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import ValidationError
from django.core.urlresolvers import reverse, reverse_lazy
from django.db.models import Q
from django.http import (
    Http404,
    HttpResponse,
    JsonResponse,
    HttpResponseRedirect)
from django.middleware.csrf import get_token
from django.shortcuts import (
    render,
    redirect,
    get_object_or_404,
)
from django.template.loader import render_to_string
from django.utils.decorators import method_decorator
from django.utils.text import slugify
from django.utils.translation import ugettext as _, get_language
from django.views.decorators.clickjacking import xframe_options_exempt
from django.views.decorators.csrf import ensure_csrf_cookie
from django.views.decorators.http import require_POST
from django.views.generic import DeleteView, View
from django.views.generic.base import TemplateResponseMixin
from braces.views import LoginRequiredMixin
from wkhtmltopdf.views import PDFTemplateView, PDFTemplateResponse

from accounts.decorators import force_login_check
from configuration.cache import get_configuration
from configuration.utils import get_filter_configuration
from configuration.utils import (
    get_configuration_index_filter,
)
from questionnaire.signals import change_questionnaire_data
from questionnaire.upload import (
    retrieve_file,
    UPLOAD_THUMBNAIL_CONTENT_TYPE,
)
from search.search import advanced_search

from .errors import QuestionnaireLockedException
from .models import Questionnaire, File, QUESTIONNAIRE_ROLES
from .summary_data_provider import get_summary_data
from .utils import (
    clean_questionnaire_data,
    get_active_filters,
    get_link_data,
    get_list_values,
    get_query_status_filter,
    get_questiongroup_data_from_translation_form,
    get_questionnaire_data_in_single_language,
    get_questionnaire_data_for_translation_form,
    handle_review_actions,
    query_questionnaires_for_link,
    query_questionnaire,
    query_questionnaires,
    get_review_config_dict)
from .view_utils import (
    ESPagination,
    get_page_parameter,
    get_pagination_parameters,
    get_paginator,
    get_limit_parameter,
)
from .conf import settings

logger = logging.getLogger(__name__)


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

    total, questionnaires = query_questionnaires_for_link(
        request, configuration, q)

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


def generic_questionnaire_view_step(
        request, identifier, step, configuration_code, page_title=''):
    """
    A generic view to show the form of a single step of a new or edited
    questionnaire.

    .. important::
        This view renders the form but has no submit logic implemented.
        It is to be used for display purposes (read-only) only!

    Args:
        ``request`` (django.http.HttpRequest): The request object.

        ``identifier`` (str): The identifier of a questionnaire.

        ``step`` (str): The code of the questionnaire category.

        ``configuration_code`` (str): The code of the questionnaire
        configuration.

    Kwargs:
        ``page_title`` (str): The page title to be used in the HTML
        template. Defaults to ``QCAT Form``.

    Returns:
        ``HttpResponse``. A rendered Http Response.
    """
    questionnaire_object = query_questionnaire(request, identifier).first()
    if questionnaire_object is None:
        raise Http404

    data = questionnaire_object.data

    questionnaire_configuration = get_configuration(configuration_code)
    category = questionnaire_configuration.get_category(step)

    if category is None:
        raise Http404

    valid = True
    show_translation = False
    edit_mode = 'view'
    original_locale = None
    current_locale = get_language()
    initial_data = get_questionnaire_data_for_translation_form(
        data, current_locale, original_locale)

    category_config, subcategories = category.get_form(
        post_data=request.POST or None, initial_data=initial_data,
        show_translation=show_translation, edit_mode=edit_mode)

    toc_content = []
    for subcategory_config, __ in subcategories:
        toc_content.append((
            subcategory_config.get('keyword'), subcategory_config.get('label'),
            subcategory_config.get('numbering')
        ))

    return render(request, 'form/category.html', {
        'subcategories': subcategories,
        'config': category_config,
        'title': page_title,
        'valid': valid,
        'edit_mode': edit_mode,
        'configuration_name': configuration_code,
        'toc_content': toc_content,
    })


class QuestionnaireEditMixin(LoginRequiredMixin, TemplateResponseMixin):
    """
    Base class for all views that are used to update a questionnaire. At least the url_namespace must be set
    when using this view.

    """
    new_identifier = 'new'
    questionnaire_configuration = None
    url_namespace = None
    configuration_code = None
    template_name = ''

    def dispatch(self, request, *args, **kwargs):
        request.session[settings.ACCOUNTS_ENFORCE_LOGIN_NAME] = True
        return super().dispatch(request, *args, **kwargs)

    @property
    def identifier(self):
        return self.kwargs.get('identifier', self.new_identifier)

    @property
    def questionnaire_configuration(self):
        return get_configuration(self.get_configuration_code())

    def get_template_names(self):
        return self.template_name or 'questionnaire/details.html'

    def get_configuration_code(self):
        return self.configuration_code or self.url_namespace

    @property
    def has_object(self):
        return self.identifier != self.new_identifier

    def get_object(self):
        """
        Returns: questionnaires.models.Questionnaire or {}
        """
        if self.has_object:
            obj = query_questionnaire(self.request, self.identifier).first()
            if not obj:
                raise Http404()
            return obj

        return {}

    @property
    def questionnaire_data(self):
        return self.object.data if self.has_object else {}

    @property
    def questionnaire_links(self):
        return self.object.links.all() if self.has_object else []

    def get_detail_url(self, step):
        """
        The detail view of the current object with #top as anchor.

        Returns: string
        """
        if self.has_object:
            url = reverse('{}:questionnaire_details'.format(self.url_namespace), args=[self.object.code])
        else:
            url = reverse('{}:questionnaire_new'.format(self.url_namespace))

        return '{url}#{step}'.format(url=url, step=step)

    def get_edit_url(self, step):
        """
        The edit view of the current object with #top as anchor.

        Returns: string
        """
        if self.has_object:
            url = reverse('{}:questionnaire_edit'.format(self.url_namespace),
                          args=[self.object.code])
        else:
            url = reverse('{}:questionnaire_new'.format(self.url_namespace))

        return '{url}#{step}'.format(url=url, step=step)


    def get_context_data(self, **kwargs):
        """
        The context data of the view. The required content is based on the previously existing views and the template
        markup.

        Returns: dict
        """
        if 'view' not in kwargs:
            kwargs['view'] = self
        return kwargs


class StepsMixin:
    """
    Get a list with all steps for current questionnaire.
    """
    def get_steps(self):
        # Flattened list with all categories.
        categories = list(chain.from_iterable(
            (section.categories for section in self.questionnaire_configuration.sections)
        ))
        return [category.keyword for category in categories]


class QuestionnaireSaveMixin(StepsMixin):
    """
    Validate and save data for object. Errors are written to
    """
    category = None
    url_namespace = None

    def dispatch(self, request, *args, **kwargs):
        self.errors = []
        self.form_has_errors = False
        return super().dispatch(request, *args, **kwargs)

    def get_success_url(self):
        return reverse('{}:questionnaire_edit'.format(self.url_namespace), kwargs={'identifier': self.object.code})

    def validate(self, subcategories, original_locale):
        """
        Validation is executed in two steps:

        - Validate given section
        - Validate complete questionnaire, with merged new section

        If either fails, an error is added to request.messages - else the object is saved and a redirect to the
        success url is returned.

        Returns: tuple (is_valid, data)

        """
        data, is_valid = self._validate_formsets(subcategories, get_language(), original_locale)
        links = get_link_data(self.questionnaire_links)

        # Check if any links were modified.
        link_questiongroups = self.category.get_link_questiongroups()
        if link_questiongroups:
            for link_qg in link_questiongroups:
                link_data = data.get(link_qg, [])
                if link_data:
                    try:
                        link_configuration_code = link_qg.rsplit('__', 1)[1]
                    except IndexError:
                        self.errors.append('There was a problem submitting the link')
                        valid = False
                        continue

                # The links initially available
                initial_links = links.get(link_configuration_code, [])
                new_links = []

                for link in link_data:
                    link_id = link.get('link_id')
                    if not link_id:
                        continue

                    try:
                        link_object = Questionnaire.with_status.not_deleted().get(pk=link_id)
                    except Questionnaire.DoesNotExist:
                        self.errors.append('The linked questionnaire with ID {} does not exist'.format(link_id))
                        valid = False
                        continue

                    # Check if the link is already in the session, in which case
                    # there is no need to get the link data again
                    link_found = False
                    for old_link in initial_links:
                        if old_link.get('id') == link_id:
                            link_found = True
                            new_links.extend(old_link)

                    if link_found is False:
                        current_link_data = get_link_data(
                            [link_object],
                            link_configuration_code=link_configuration_code
                        )
                        new_links.extend(current_link_data.get(
                            link_configuration_code))

                links[link_configuration_code] = new_links

        if not is_valid:
            return is_valid, data
        else:
            # Links will be saved only when everything is valid.
            self.links = links
            # Merge validated data to complete questionnaire and validate this again.
            return self.merge_and_validate(data)

    def merge_and_validate(self, data):
        """
        Merge data from current section to questionnaire and validate complete questionnaire data.

        Args:
            data: dict

        Returns:
            tuple: is_valid, data

        Todo: discuss with lukas: what happens if the section data is valid, but the whole questionnaire is invalid?

        """
        if self.has_object:
            self.object.data.update(data)
            data = self.object.data

        questionnaire_data, errors = clean_questionnaire_data(data, self.questionnaire_configuration)
        if errors:
            self.errors.extend(errors)
        return not bool(self.errors), questionnaire_data

    def can_lock_object(self):
        # Try to lock questionnaire, raise an error if it is locked already.
        try:
            Questionnaire().lock_questionnaire(self.identifier, self.request.user)
        except QuestionnaireLockedException as e:
            self.errors.append(e)
            return False
        return True

    def save(self, subcategories, original_locale):
        """
        Validate and save the questionnaire.
        """
        is_valid, data = self.validate(subcategories, original_locale)

        if not is_valid or not self.can_lock_object():
            return self.form_invalid()
        else:
            return self.form_valid(data)

    def form_valid(self, data: dict):
        """
        Save the new questionnaire data and create a log for the change.
        """
        try:
            questionnaire = Questionnaire.create_new(
                configuration_code=self.get_configuration_code(), data=data, user=self.request.user,
                previous_version=self.object if self.has_object else None, old_data=None
            )
            self.object = questionnaire
        except ValidationError as e:
            self.errors.append(e)
            return self.form_invalid()

        self.save_questionnaire_links()
        questionnaire.unlock_questionnaire()
        messages.success(self.request, _('Data successfully saved.'))
        change_questionnaire_data.send(
            sender=settings.NOTIFICATIONS_EDIT_CONTENT,
            questionnaire=questionnaire,
            user=self.request.user
        )
        return HttpResponseRedirect(self.get_success_url())

    def form_invalid(self):
        """
        Some errors are non-form errors and are displayed with as messages. The context (or better: the templates)
        doesn't display the errors yet.
        """
        for error in self.errors:
            messages.error(self.request, error)
        return self.render_to_response(self.get_context_data(errors=self.errors))

    def _validate_formsets(self, nested_formsets, current_locale, original_locale):
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
                self.form_has_errors = True
                return None, False

            for f in formset.forms:
                questiongroup_keyword = f.prefix.split('-')[0]
                cleaned_data = get_questiongroup_data_from_translation_form(
                    f.cleaned_data, current_locale, original_locale
                )
                try:
                    data[questiongroup_keyword].append(cleaned_data)
                except KeyError:
                    data[questiongroup_keyword] = [cleaned_data]

        return data, True

    def get_success_url_next_section(self, identifier, current):
        """
        The 'step' we need is the keyword of the next 'category'. This category is part of the section.

        Args:
            current: string (the current step)
            identifier: string to identify the questionnaire in the url pattern

        Returns:
            url

        """

        # Current or next step may not exist - use the default
        # redirect.
        steps = self.get_steps()
        with contextlib.suppress(ValueError, IndexError):
            current_step = steps.index(current)
            url = reverse('{}:questionnaire_new_step'.format(self.url_namespace), kwargs={
                'identifier': identifier,
                'step': steps[current_step + 1]
            })
            return HttpResponseRedirect(url)

    def save_questionnaire_links(self):
        """
        Save the linked questionnaires to for the current object.
        """
        if not hasattr(self, 'links') or not self.links:
            return

        # Collect the IDs of all (newly) linked questionnaires
        linked_ids = []
        for __, linked_questionnaires in self.links.items():
            linked_ids.extend([x.get('id') for x in linked_questionnaires])

        # Remove all currently linked questionnaires which are not in this list
        for removed in self.object.links.exclude(id__in=linked_ids):
            self.object.remove_link(removed)

        # Add links to all questionnaires in the list
        for linked in linked_ids:
            with contextlib.suppress(Questionnaire.DoesNotExist):
                link = Questionnaire.objects.get(pk=linked)
                self.object.add_link(link)


class GenericQuestionnaireMapView(TemplateResponseMixin, View):
    """
    A generic view to show the map of a questionnaire (in a modal)
    """
    http_method_names = ['get']
    template_name = 'details/modal_map.html'
    url_namespace = None

    def get_object(self):
        questionnaire_object = query_questionnaire(
            self.request, self.kwargs.get('identifier')).first()
        if questionnaire_object is None:
            raise Http404()
        return questionnaire_object

    @xframe_options_exempt
    def get(self, request, *args, **kwargs):
        questionnaire_object = self.get_object()

        configuration = get_configuration(configuration_code=self.url_namespace)
        geometry = configuration.get_questionnaire_geometry(
            questionnaire_object.data)

        context = {
            'geometry': geometry,
        }

        return self.render_to_response(context=context)


class GenericQuestionnaireView(QuestionnaireEditMixin, StepsMixin, View):
    """
    Refactored function based view: generic_questionnaire_new
    """
    http_method_names = ['get']

    @method_decorator(ensure_csrf_cookie)
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get(self, request, *args, **kwargs):
        """
        Display the questionnaire overview.
        """
        self.object = self.get_object()

        data = get_questionnaire_data_in_single_language(
            questionnaire_data=self.questionnaire_data, locale=get_language(),
            original_locale=self.object.original_locale if self.object else None
        )

        if self.has_object:
            roles, permissions = self.object.get_roles_permissions(
                self.request.user)
        else:
            # User is always compiler of new questionnaires.
            role = settings.QUESTIONNAIRE_COMPILER
            roles = [(role, dict(QUESTIONNAIRE_ROLES).get(role))]
            permissions = ['edit_questionnaire']

        csrf_token = get_token(self.request) if 'edit_questionnaire' in permissions else None

        images = self.questionnaire_configuration.get_image_data(data).get('content', [])

        can_edit = None
        blocked_by = None
        # Display a message regarding the state for editing (locked / available)
        if self.has_object:
            can_edit = self.object.can_edit(request.user)
            level, message = self.object.get_blocked_message(request.user)
            blocked_by = message
            messages.add_message(request, level, message)

        # TODO: Highlight changes disabled.
        # For the time being, the function to show changes has been
        # disabled. Delete the following line to reenable it.
        edited_questiongroups = []

        # Url when switching the mode - go to the detail view.
        url = self.get_detail_url(step='') if self.has_object else ''

        review_config = self.get_review_config(
            permissions=permissions, roles=roles, url=url,
            blocked_by=blocked_by if not can_edit else False,
            view_mode='edit'
        )
        if not self.has_object:
            review_config.update({
                'data_type': self.url_namespace,
                'first_section_url': reverse('{}:questionnaire_new_step'.format(self.url_namespace), kwargs={
                    'identifier': self.identifier, 'step': self.get_steps()[0]
                })
            })

        sections = self.questionnaire_configuration.get_details(
            data, permissions=permissions,
            edit_step_route='{}:questionnaire_new_step'.format(
                self.url_namespace),
            questionnaire_object=self.object or None,
            csrf_token=csrf_token,
            edited_questiongroups=edited_questiongroups,
            view_mode='edit',
            links=self.get_links(),
            review_config=review_config,
            user=request.user,
        )

        context = {
            'images': images,
            'sections': sections,
            'questionnaire_identifier': self.identifier,
            'url_namespace': self.url_namespace,
            'permissions': permissions,
            'edited_questiongroups': edited_questiongroups,
            'view_mode': 'edit',
            'is_blocked': not can_edit,
            'toc_content': self.questionnaire_configuration.get_toc_data(),
            'has_content': bool(data),
            'review_config': review_config,
            'questionnaires_in_progress': self.questionnaires_in_progress(),
            'base_template': '{}/base.html'.format(self.url_namespace),
        }
        return self.render_to_response(context=context)

    def get_detail_url(self, step):
        return super().get_detail_url(step='top')

    def get_review_config(self, permissions, roles, url, **kwargs):
        """
        Create a dict with the review_config, this is required for proper display
        of the review panel.

        Args:
            permissions: list
            url: string
            **kwargs:

        Returns: dict

        """
        return get_review_config_dict(
            status=self.object.status if self.has_object else 0,
            token=get_token(self.request),
            permissions=permissions,
            roles=roles,
            view_mode=kwargs.get('view_mode', 'view'),
            url=url,
            is_blocked=bool(kwargs.get('blocked_by', False)),
            blocked_by=kwargs.get('blocked_by', ''),
            form_url=self.get_detail_url(step=''),
            has_release=self.has_release()
        )

    def questionnaires_in_progress(self):
        """
        Get all questionnaires that given user is currently working on.

        Returns:
            queryset

        """
        return Questionnaire.with_status.not_deleted().filter(
            status=settings.QUESTIONNAIRE_DRAFT,
            questionnairemembership__user=self.request.user,
            questionnairemembership__role__in=[
                settings.QUESTIONNAIRE_COMPILER, settings.QUESTIONNAIRE_EDITOR
            ]
        )

    def get_links(self):
        """
        Prepare links as expected by the template.

        Returns: dict
        """
        if not self.has_object:
            return None

        linked_questionnaires = self.object.links.filter(configurations__isnull=False)
        links_by_configuration = collections.defaultdict(list)

        for linked in linked_questionnaires:
            links_by_configuration[linked.configurations.first().code].append(linked)

        link_display = {}
        for configuration, links in links_by_configuration.items():
            link_display[configuration] = get_list_values(
                configuration_code=configuration, questionnaire_objects=links, with_links=False
            )
        return link_display

    def has_release(self):
        return self.has_object and self.object.has_release


class GenericQuestionnaireStepView(QuestionnaireEditMixin, QuestionnaireSaveMixin, View):
    """
    A section of the questionnaire.
    """
    edit_mode = 'edit'
    template_name = 'form/category.html'

    def set_attributes(self):
        """
        Shared calls (pseudo setup) for get and post
        """
        self.object = self.get_object()
        self.category = self.questionnaire_configuration.get_category(self.kwargs['step'])
        if not self.category:
            raise Http404()
        self.category_config, self.subcategories = self.get_subcategories()

    def get(self, request, *args, **kwargs):
        """
        Display the form for the selected step,
        """
        self.set_attributes()
        if self.has_object:
            Questionnaire.lock_questionnaire(self.object.code, self.request.user)
        return self.render_to_response(context=self.get_context_data())

    def post(self, request, *args, **kwargs):
        """
        Validate and save the data. If valid, a redirect to the .get() view is returned (Post-Redirect-Get)

        Returns: HttpResponse

        """
        self.set_attributes()
        original_locale, show_translation = self.get_locale_info()
        return self.save(self.subcategories, original_locale)

    def get_success_url(self):
        url = super().get_success_url()
        return '{}#{}'.format(url, self.kwargs['step'])

    def form_valid(self, data):
        """
        Handle special case if the user clicks on 'save and go to next section'

        """
        response = super().form_valid(data)

        if self.request.POST.get('goto-next-section', '') == 'true':
            next_step = self.get_success_url_next_section(self.object.code, self.kwargs['step'])
            if next_step:
                return next_step

        return response

    def get_locale_info(self):
        """
        Get the original locale of the current object.

        Returns: tuple (original_locale, show_translation)
        """
        original_locale = None
        if self.has_object:
            original_locale = self.object.original_locale

        show_translation = (original_locale is not None and get_language() != original_locale)
        return original_locale, show_translation

    def get_subcategories(self):
        """
        Returns: tuple (category_config, subcategories)
        """
        original_locale, show_translation = self.get_locale_info()

        initial_data = get_questionnaire_data_for_translation_form(
            self.object.data if self.has_object else {}, get_language(), original_locale
        )
        initial_links = get_link_data(self.questionnaire_links)

        category_config, subcategories = self.category.get_form(
            post_data=self.request.POST or None,
            initial_data=initial_data, show_translation=show_translation,
            edit_mode=self.edit_mode,
            edited_questiongroups=[], initial_links=initial_links,
        )
        return category_config, subcategories

    def get_toc_content(self):
        toc_content = []
        for subcategory_config, __ in self.subcategories:
            toc_content.append((
                subcategory_config.get('keyword'), subcategory_config.get('label'),
                subcategory_config.get('numbering')
            ))
        return toc_content

    def get_context_data(self, **kwargs):
        """
        Provide all info required to display a single step of the form.

        Returns: dict
        """
        ctx = super().get_context_data(**kwargs)

        view_url = ''
        if self.has_object:
            view_url = reverse('{}:questionnaire_view_step'.format(self.url_namespace),
                               args=[self.identifier, self.kwargs['step']])

        ctx.update({
            'subcategories': self.subcategories,
            'config': self.category_config,
            'content_subcategories_count': len([c for c in self.subcategories if c[1] != []]),
            'title': _('QCAT Form'),
            'overview_url': self.get_edit_url(self.kwargs['step']),
            'valid': not self.form_has_errors,
            'configuration_name': self.category_config.get('configuration', self.url_namespace),
            'edit_mode': self.edit_mode,
            'view_url': view_url,
            'toc_content': self.get_toc_content(),
        })
        return ctx


@ensure_csrf_cookie
def generic_questionnaire_details(
        request, identifier, configuration_code, url_namespace):
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
        questionnaire_object.data, get_language(),
        original_locale=questionnaire_object.original_locale)

    if request.method == 'POST':
        review = handle_review_actions(
            request, questionnaire_object, configuration_code)
        if isinstance(review, HttpResponse):
            return review
        return redirect(
            '{}:questionnaire_details'.format(url_namespace),
            questionnaire_object.code)

    roles_permissions = questionnaire_object.get_roles_permissions(request.user)
    roles = roles_permissions.roles
    permissions = roles_permissions.permissions

    review_config = {}
    if request.user.is_authenticated():
        # Show the review panel only if the user is logged in and if the
        # version shown is not active (public).
        blocked_by = None
        if not questionnaire_object.can_edit(request.user):
            lvl, blocked_by = questionnaire_object.get_blocked_message(request.user)

        # The first tab or the review panel is either welcome or edit - depending if this object has a public version.
        has_release = questionnaire_object.status == settings.QUESTIONNAIRE_PUBLIC or Questionnaire.objects.filter(
            code=questionnaire_object.code, status=settings.QUESTIONNAIRE_PUBLIC).exists()

        review_config = get_review_config_dict(
            status=questionnaire_object.status,
            token=get_token(request),
            permissions=permissions,
            roles=roles,
            view_mode='view',
            url=reverse('{}:questionnaire_edit'.format(url_namespace),
                        kwargs={'identifier': questionnaire_object.code}),
            is_blocked=bool(blocked_by),
            blocked_by=blocked_by,
            form_url=reverse('{}:questionnaire_details'.format(url_namespace),
                             kwargs={'identifier': questionnaire_object.code}),
            has_release=has_release
        )

        if 'assign_questionnaire' in review_config.get('permissions', []):
            if questionnaire_object.status == settings.QUESTIONNAIRE_DRAFT:
                review_config['editors'] = questionnaire_object.\
                    get_users_by_role('editor')
            elif questionnaire_object.status \
                    == settings.QUESTIONNAIRE_SUBMITTED:
                review_config['reviewers'] = questionnaire_object.\
                    get_users_by_role('reviewer')
            elif questionnaire_object.status == settings.QUESTIONNAIRE_REVIEWED:
                review_config['publishers'] = questionnaire_object. \
                    get_users_by_role('publisher')

    images = questionnaire_configuration.get_image_data(
        data).get('content', [])

    links_by_configuration = {}
    status_filter = get_query_status_filter(request)
    for linked in questionnaire_object.links.filter(status_filter):
        configuration = linked.configurations.first()
        if configuration is None:
            continue
        if configuration.code not in links_by_configuration:
            links_by_configuration[configuration.code] = [linked]
        else:
            # Add each questionnaire (by code) only once to avoid having
            # multiple (pending) versions of the same questionnaire
            # shown.
            found = False
            for link in links_by_configuration[configuration.code]:
                if link.code == linked.code:
                    found = True
            if found is False:
                links_by_configuration[configuration.code].append(linked)

    link_display = {}
    for configuration, links in links_by_configuration.items():
        link_display[configuration] = get_list_values(
            configuration_code=configuration, questionnaire_objects=links,
            with_links=False)

    sections = questionnaire_configuration.get_details(
        data=data, permissions=permissions, review_config=review_config,
        questionnaire_object=questionnaire_object, links=link_display,
        user=request.user if request.user.is_authenticated() else None
    )

    return render(request, 'questionnaire/details.html', {
        'images': images,
        'sections': sections,
        'questionnaire_identifier': identifier,
        'permissions': permissions,
        'view_mode': 'view',
        'toc_content': questionnaire_configuration.get_toc_data(),
        'review_config': review_config,
        'base_template': '{}/base.html'.format(url_namespace),
    })


def generic_questionnaire_list_no_config(
        request, user=None, moderation_mode=None):
    """
    A generic view to show a list of Questionnaires. Similar to
    :func:`generic_questionnaire_list` but with the following
    differences:

    * No configuration is used, meaning that questionnaires from all
      configurations are queried.

    * No (attribute) filter configuration is created and provided.

    * Special status filters are used: In moderation mode
      (``moderation=True``), only pending versions are returned. Users
      see their own versions (all statuses). Else the default status
      filter is used.

    * Always return the template values as a dictionary.

    Args:
        ``request`` (django.http.HttpRequest): The request object.

    Kwargs:
        ``user`` (``accounts.models.User``): If provided, show only
        Questionnaires in which the user is a member of.

        ``moderation`` (bool): If ``True``, always only show ``pending``
         Questionnaires if the current user has moderation
        permission.

    Returns:
        ``dict``. A dictionary with template values to be used in a list
        template.
    """
    limit = get_limit_parameter(request)
    page = get_page_parameter(request)
    is_current_user = request.user is not None and request.user == user

    # Determine the status filter
    if moderation_mode is not None:
        # Moderators always have a special moderation status filter
        status_filter = get_query_status_filter(
            request, moderation_mode=moderation_mode)
    elif is_current_user is True:
        # The current user has no status filter (sees all statuses)
        status_filter = Q()
    else:
        # Else use the default status filter (will be applied in
        # :func:`query_questionnaires`)
        status_filter = None

    questionnaire_objects = query_questionnaires(
        request, 'all', only_current=False,
        limit=None, user=user, status_filter=status_filter)

    questionnaires, paginator = get_paginator(
        questionnaire_objects, page, limit)

    status_filter = get_query_status_filter(request)
    list_values = get_list_values(
        configuration_code='wocat',
        questionnaire_objects=questionnaires, status_filter=status_filter)

    template_values = {
        'list_values': list_values,
        'is_current_user': is_current_user,
        'list_user': user,
        'is_moderation': moderation_mode,
    }

    # Add the pagination parameters
    pagination_params = get_pagination_parameters(
        request, paginator, questionnaires)
    template_values.update(pagination_params)

    return template_values


def generic_questionnaire_list(
        request, configuration_code, template=None, filter_url='', limit=None,
        only_current=False):
    """
    A generic view to show a list of Questionnaires.

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

    Returns:
        ``HttpResponse``. A rendered Http Response.
    """
    configuration_codes = get_configuration_index_filter(configuration_code)
    configurations = [get_configuration(code) for code in configuration_codes]


    # Get the filters and prepare them to be passed to the search.
    active_filters = get_active_filters(configurations, request.GET)
    query_string = ''
    filter_params = []
    for active_filter in active_filters:
        filter_type = active_filter.get('type')
        if filter_type in ['_search']:
            query_string = active_filter.get('value', '')
        elif filter_type in [
                'checkbox', 'image_checkbox', '_date', '_flag', 'select_type',
                'select_model', 'radio', 'bool']:
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

    search_configuration_codes = get_configuration_index_filter(
        configuration_code, only_current=only_current,
        query_param_filter=tuple(request.GET.getlist('type')))

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
    filter_configuration = get_filter_configuration(configuration_code)

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
@force_login_check
def generic_file_upload(request):
    """
    A view to handle file uploads. Can only be called with POST requests
    and returns a JSON.

    Args:
        request (django.http.HttpRequest): The request object. Only
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
        file_object = File.handle_upload(file)
    except Exception as e:
        ret['msg'] = str(e)
        return JsonResponse(ret, status=400)

    file_data = File.get_data(file_object=file_object)
    ret = {
        'success': True,
        'uid': file_data.get('uid'),
        'interchange': file_data.get('interchange'),
        'url': file_data.get('url'),
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
        request (django.http.HttpRequest): The request object.

        action (str): The action to perform with the file. Available
        options are ``display``, ``download`` and ``interchange``.

        uid (str): The UUID of the file object.

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
    file_data = File.get_data(file_object=file_object)

    if action == 'interchange':
        return HttpResponse(file_data.get('interchange'))

    thumbnail = request.GET.get('format')
    try:
        file, filename = retrieve_file(file_object, thumbnail=thumbnail)
    except:
        raise Http404()

    content_type = file_data.get('content_type')
    if thumbnail is not None:
        content_type = UPLOAD_THUMBNAIL_CONTENT_TYPE

    response = HttpResponse(file, content_type=content_type)
    if action == 'download':
        response['Content-Disposition'] = 'attachment; filename={}'.format(
            filename)
        response['Content-Length'] = file_data.get('size')

    return response


class QuestionnaireDeleteView(DeleteView):
    """
    Confirm and pseudo-delete questionnaire object.

    """
    model = Questionnaire
    slug_field = 'code'
    slug_url_kwarg = 'identifier'
    success_url = reverse_lazy('account_questionnaires')

    def delete(self, request, *args, **kwargs):
        """
        Update deleted flag for given questionnaire and add message.
        """
        self.object = self.get_object()
        success_url = self.get_success_url()
        messages.success(
            self.request, _('Successfully removed questionnaire')
        )
        self.object.is_deleted=True
        self.object.save()
        return HttpResponseRedirect(success_url)


class CachedPDFTemplateResponse(PDFTemplateResponse):
    """
    Creating the pdf includes two resource-heavy processes:
    - extracting the json to markup (frontend)
    - call to wkhtmltopdf (backend)

    Therefore, the content is created only once per filename (which should
    distinguish between new questionnaire edits). This only works with
    reasonably precise file names!
    """

    @property
    def rendered_content(self):
        file_path = join(settings.SUMMARY_PDF_PATH, self.filename)
        if isfile(file_path):
            with contextlib.suppress(Exception) as e:
                # Catch any kind of error and log it. PDF is created from
                # scratch again.
                logger.warn("Couldn't open pdf summary from disk: {}".format(e))
                return open(file_path, 'rb').read()

        content = super().rendered_content
        with contextlib.suppress(Exception) as e:
            # Again, intentionally catch any kind of exception.
            logger.warn("Couldn't write pdf summary from disk: {}".format(e))
            open(file_path, 'wb').write(content)
        return content


class QuestionnaireSummaryPDFCreateView(PDFTemplateView):
    """
    Put the questionnaire data to the context and return the rendered pdf.
    """
    # Activate this as soon as frontend is finished.
    # response_class = CachedPDFTemplateResponse

    # Refactor this when more than one summary type is available.
    summary_type = 'full'
    base_template_path = 'questionnaire/summary/'

    def get(self, request, *args, **kwargs):
        self.questionnaire = self.get_object(id=self.kwargs['id'])
        return super().get(request, *args, **kwargs)

    def get_template_names(self):
        return '{}/layout/{}.html'.format(self.base_template_path, self.code)

    def get_filename(self) -> str:
        """
        The filename is specific enough to be used as 'pseudo cache-key' in the
        CachedPDFTemplateResponse.
        """
        return 'wocat-{identifier}-{summary_type}-summary-{update}.pdf'.format(
            summary_type=self.summary_type,
            identifier=self.questionnaire.id,
            update=self.questionnaire.updated.strftime('%Y-%m-%d-%H:%m')
        )

    def get_object(self, id: int) -> Questionnaire:
        """
        Get questionnaire and check status / permissions.
        """

        status_filter = get_query_status_filter(self.request)
        status_filter &= Q(id=id)
        obj = Questionnaire.with_status.not_deleted().filter(
            Q(id=id), status_filter
        ).distinct()
        if not obj.exists() or obj.count() != 1:
            raise Http404
        return obj.first()

    def get_prepared_data(self, questionnaire: Questionnaire) -> dict:
        """
        Load the prepared JSON for given object in the current language.
        """
        data = get_questionnaire_data_in_single_language(
            questionnaire_data=questionnaire.data,
            locale=get_language(),
            original_locale=questionnaire.original_locale
        )
        self.code = questionnaire.configurations.filter(active=True).first().code
        return get_summary_data(
            config=get_configuration(configuration_code=self.code),
            summary_type=self.summary_type,
            **data
        )

    def get_context_data(self, **kwargs):
        """
        Dump json to the context, the markup for the pdf is created with a js
        library in the frontend.
        """
        context = super().get_context_data(**kwargs)
        default_block_template = '{}block/default.html'.format(
            self.base_template_path,
        )
        data = self.get_prepared_data(self.questionnaire)
        rendered_blocks = []
        for block in data:
            rendered_elements = []
            elements = block.pop('elements')
            for element in elements:
                rendered_elements.append(
                    render_to_string(
                        '{}element/default.html'.format(self.base_template_path),
                        context=element
                    )
                )

            block_template_name = '{}block/{}.html'.format(
                self.base_template_path,
                slugify(block['title'])
            )
            block.update({'rendered_elements': rendered_elements})
            rendered_blocks.append(
                render_to_string(
                    template_name=[block_template_name, default_block_template],
                    context={**block}
                )
            )
        context['rendered_blocks'] = rendered_blocks
        return context

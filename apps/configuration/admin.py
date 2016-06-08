import json
from django import forms
from django.conf import settings
from django.contrib import admin
from django.utils.html import format_html

from configuration.models import (
    Category,
    Configuration,
    Key,
    Project,
    Translation,
    Institution,
)


class CustomFormWithJsonData(forms.ModelForm):
    """
    The base class for a form in the administration interface for a
    model containing a JSON field called ``data``. Inherit from this
    class to add a validation of the ``data`` field, checking for valid
    JSON notation.
    """
    def clean_data(self):
        """
        Check if the value in field "data" is a valid JSON.

        Raises:
            ``ValidationError``. An error is raised if the field does
            not contain a valid JSON.

        Returns:
            ``dict``. The value in field "data" loaded as JSON.
        """
        try:
            data = json.loads(self.cleaned_data['data'])
        except ValueError:
            raise forms.ValidationError('Invalid JSON!')
        return data


class CustomConfigurationForm(CustomFormWithJsonData):
    """
    A form to create or update a
    :class:`configuration.models.Configuration` in the administration
    interface. The ``base_code`` is rendered as dropdown allowing only
    the selection of an existing code.
    """
    def __init__(self, *args, **kwargs):
        super(CustomConfigurationForm, self).__init__(*args, **kwargs)

        # Dynamically refine the choices for the base_code. Query the
        # distinct codes of existing configurations.
        codes = Configuration.objects.order_by().values_list('code').distinct()
        base_code_choices = (('', '-'),)
        for code in codes:
            base_code_choices = base_code_choices + ((code[0], code[0]),)

        self.fields['base_code'].choices = base_code_choices

    base_code = forms.ChoiceField(
        required=False, widget=forms.Select,
        help_text=Configuration._meta.get_field('base_code').help_text)


@admin.register(Configuration)
class ConfigurationAdmin(admin.ModelAdmin):
    """
    The representation of :class:`configuration.models.Configuration` in
    the administration interface.
    """
    form = CustomConfigurationForm

    list_display = (
        'code', 'name', 'description', 'created', 'active', 'base_code')
    list_filter = ('code',)
    ordering = ('code',)
    change_list_template = 'admin/change_list_filter_sidebar.html'
    change_list_filter_template = 'admin/filter_listing.html'

    fieldsets = (
        (None, {'fields': ('code', 'name', 'description', 'created')}),
        ('Configuration', {'fields': ('data', 'base_code')}),
        ('Activation', {'fields': ('active', 'activated')}),
    )
    readonly_fields = ('created', 'activated')


@admin.register(Key)
class KeyAdmin(admin.ModelAdmin):
    """
    The representation of :class:`configuration.models.Key` in the
    administration interface.
    """
    list_display = ('keyword', 'translation', 'type_')
    ordering = ('keyword',)
    search_fields = ('keyword',)


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    """
    The representation of :class:`configuration.models.Category` in the
    administration interface.
    """
    list_display = ('keyword', 'translation')
    ordering = ('keyword',)
    search_fields = ('keyword',)


class CategoryInlineReadonly(admin.TabularInline):
    """
    The readonly inline form for a
    :class:`configuration.models.Category`. Used for example in the form
    of :class:`configuration.models.Translation` to display the
    categories with the current translation.
    """
    model = Category
    readonly_fields = ('keyword',)
    extra = 0
    can_delete = False

    def has_add_permission(self, request):
        return False


class KeyInlineReadonly(admin.TabularInline):
    """
    The readonly inline form for a
    :class:`configuration.models.Key`. Used for example in the form of
    :class:`configuration.models.Translation` to display the keys with
    the current translation.
    """
    model = Key
    fields = ('keyword',)
    readonly_fields = ('keyword',)
    extra = 0
    can_delete = False

    def has_add_permission(self, request):
        return False


class CustomTranslationForm(CustomFormWithJsonData):
    """
    A form to create or update a
    :class:`configuration.models.Translation` in the administration
    interface. The ``translation_type`` is rendered as dropdown allowing
    only the selection of a valid type.
    """
    def __init__(self, *args, **kwargs):
        super(CustomTranslationForm, self).__init__(*args, **kwargs)

        # Dynamically refine the choices for the translation_type.
        translation_types = (('', '-'),)
        for t_type in Translation.get_translation_types():
            translation_types = translation_types + ((t_type, t_type),)

        self.fields['translation_type'].choices = translation_types

    translation_type = forms.ChoiceField(
        required=False, widget=forms.Select,
        help_text=Translation._meta.get_field('translation_type').help_text)


@admin.register(Translation)
class TranslationAdmin(admin.ModelAdmin):
    """
    The representation of :class:`configuration.models.Translation` in
    the administration interface.
    """
    form = CustomTranslationForm

    # Translation columns are populated dynamically
    list_display = ('translation_type', 'translations')
    list_filter = ('translation_type',)
    ordering = ('translation_type',)
    change_list_template = 'admin/change_list_filter_sidebar.html'
    change_list_filter_template = 'admin/filter_listing.html'
    inlines = (CategoryInlineReadonly, KeyInlineReadonly)

    def translations(self, obj):
        translations = []
        for locale in [l[0] for l in settings.LANGUAGES]:
            translations.append('<strong>{}</strong>: {}'.format(
                locale, obj.get_translation(locale)))
        return format_html('<br/>'.join(translations))


@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    """
    The representation of :class:`configuration.models.Project` in the
    administration interface.
    """
    list_display = ('id', 'name', 'abbreviation', 'active',)
    list_filter = ('active',)
    search_fields = ('name', 'abbreviation',)


@admin.register(Institution)
class InstitutionAdmin(admin.ModelAdmin):
    """
    The representation of :class:`configuration.models.Institution` in the
    administration interface.
    """
    list_display = ('id', 'name', 'abbreviation', 'country', 'active',)
    list_filter = ('active', 'country')
    search_fields = ('name', 'abbreviation',)

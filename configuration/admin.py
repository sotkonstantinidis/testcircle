import json
from django import forms
from django.contrib import admin

from configuration.models import Configuration


class CustomConfigurationForm(forms.ModelForm):
    """
    A form to create or update a
    :class:`configuration.models.Configuration` in the administration
    interface.
    """

    def __init__(self, *args, **kwargs):
        super(CustomConfigurationForm, self).__init__(*args, **kwargs)

        # Dynamically refine the choices for the base_code. Query the distinct
        # codes of existing configurations.
        codes = Configuration.objects.order_by().values_list('code').distinct()
        base_code_choices = (('', '-'),)
        for code in codes:
            base_code_choices = base_code_choices + ((code[0], code[0]),)

        self.fields['base_code'].choices = base_code_choices

    base_code = forms.ChoiceField(
        required=False, widget=forms.Select,
        help_text=Configuration._meta.get_field('base_code').help_text)

    def clean_data(self):
        """
        Check if the value in field "data" is a valid JSON.
        """
        try:
            data = json.loads(self.cleaned_data['data'])
        except ValueError:
            raise forms.ValidationError('Invalid JSON!')
        return data


class ConfigurationAdmin(admin.ModelAdmin):
    """
    The representation of :class:`configuration.models.Configuration` in
    the administration interface.
    """
    form = CustomConfigurationForm

    list_display = (
        'code', 'name', 'description', 'created', 'active', 'base_code',
        'data')
    list_filter = ('code',)
    ordering = ('code',)

    fieldsets = (
        (None, {'fields': ('code', 'name', 'description', 'created')}),
        ('Configuration', {'fields': ('data', 'base_code')}),
        ('Activation', {'fields': ('active', 'activated')}),
    )
    readonly_fields = ('created', 'activated')

admin.site.register(Configuration, ConfigurationAdmin)

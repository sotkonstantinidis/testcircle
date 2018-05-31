from django.contrib import admin
from django.utils.safestring import mark_safe
from django.utils.translation import ugettext_lazy as _

from configuration.models import Configuration
from .models import Lock, Questionnaire


@admin.register(Lock)
class LockAdmin(admin.ModelAdmin):

    def questionnaire_code(self):
        return self.questionnaire.code

    list_display = ['id', questionnaire_code, 'user', 'start', 'is_finished']


class NewEditionFilter(admin.SimpleListFilter):
    title = _('Latest edition')
    parameter_name = 'has_new_edition'

    def lookups(self, request, model_admin):
        return (
            (True, _('Yes')),
            (False, _('No')),
        )

    def queryset(self, request, queryset):
        """
        Filter for latest configurations.
        """
        if self.value() is None:
            return queryset

        latest_configurations = Configuration.objects.distinct(
            'code'
        ).order_by(
            'code', '-created'
        ).values_list(
            'id', flat=True
        )
        if self.value() == 'True':
            return queryset.exclude(configuration_id__in=latest_configurations)
        else:
            return queryset.filter(configuration__id__in=latest_configurations)


@admin.register(Questionnaire)
class QuestionnaireAdmin(admin.ModelAdmin):
    list_display = ['id', 'code', 'get_name', 'status', 'updated', 'has_new_edition', 'edit_url']
    list_filter = ['configuration', 'status', NewEditionFilter]

    def has_new_edition(self, obj):
        return obj.configuration_object.has_new_edition
    has_new_edition.boolean = True

    def edit_url(self, obj):
        return mark_safe(
            f'<a href="{obj.get_edit_url()}" target="_blank">Edit</a>'
        )

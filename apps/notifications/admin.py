from django.contrib import admin

from .models import Log


@admin.register(Log)
class MessageAdmin(admin.ModelAdmin):
    list_display = ['__str__', 'action', 'catalyst', 'created']
    list_filter = ['questionnaire']

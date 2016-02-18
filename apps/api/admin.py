from django.contrib import admin

from .models import RequestLog


@admin.register(RequestLog)
class RequestLogAdmin(admin.ModelAdmin):
    list_filter = ('user', 'access', )
    date_hierarchy = 'access'
    list_display = ['__str__', 'access']

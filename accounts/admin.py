from django import forms
from django.contrib import admin
from django.contrib.auth import admin as auth_admin
from django.contrib.auth.models import Group

from accounts.models import User


class CustomUserChangeForm(forms.ModelForm):
    """
    A form for updating users.
    """
    def clean_password(self):
        """
        A stub function to prevent errors when validating the form.
        """
        pass


class UserAdmin(auth_admin.UserAdmin):
    form = CustomUserChangeForm

    list_display = (
        'email', 'name', 'id', 'is_superuser', 'date_joined', 'last_login')
    list_filter = ('is_superuser', 'groups')

    readonly_fields = ('email',)
    fieldsets = (
        (None, {'fields': ('email', 'name')}),
        ('Permissions', {'fields': ('is_superuser', 'groups')}),
    )

    search_fields = ('email',)
    ordering = ('email',)
    filter_horizontal = ('groups',)

    # No new users can be added.
    def has_add_permission(self, request):
        return False

# Groups cannot be managed by the admin interface
admin.site.unregister(Group)

admin.site.register(User, UserAdmin)

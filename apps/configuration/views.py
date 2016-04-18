# -*- coding: utf-8 -*-
from braces.views import LoginRequiredMixin, SuperuserRequiredMixin
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.management import call_command
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import RedirectView
from django.utils.translation import ugettext_lazy as _

from accounts.decorators import force_login_check
from configuration.cache import delete_configuration_cache
from configuration.models import Configuration


@login_required
@force_login_check
def delete_caches(request):
    """
    Delete all the caches.

    Args:
        ``request`` (django.http.HttpRequest): The request object.

    Returns:
        ``HttpResponse``. A rendered Http Response (redirected to the
        search admin home page).
    """
    if request.user.is_superuser is not True:
        raise PermissionDenied()

    active_configurations = Configuration.objects.filter(active=True)
    for configuration in active_configurations:
        delete_configuration_cache(configuration)

    messages.success(request, 'Caches deleted.')

    return redirect('search:admin')


class BuildAllCachesView(LoginRequiredMixin, SuperuserRequiredMixin,
                         RedirectView):
    """
    Build cache for all questionnaires.
    """
    url = reverse_lazy('search:admin')
    permanent = False
    login_url = reverse_lazy('login')

    def get(self, request, *args, **kwargs):
        self.build_caches(request)
        return super().get(request, *args, **kwargs)

    def build_caches(self, request):
        """
        Build the cache for all active configurations.

        """
        call_command('build_config_caches')

        messages.success(request, _(u"Built configuration caches."))

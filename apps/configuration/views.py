# -*- coding: utf-8 -*-
import contextlib
import importlib.util
from pathlib import Path

from braces.views import LoginRequiredMixin, SuperuserRequiredMixin
from django.conf import settings
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.core.management import call_command
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import redirect
from django.views.generic import RedirectView, TemplateView
from django.utils.translation import ugettext_lazy as _

from .cache import delete_configuration_cache
from .editions.base import Edition
from .models import Configuration


@login_required
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

    for configuration in Configuration.objects.all():
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


class EditionNotesView(TemplateView):
    """
    'Release notes' for configurations.

    """
    template_name = 'configuration/edition_notes.html'
    edition_root = Path(settings.BASE_DIR, 'apps', 'configuration', 'editions')
    edition_base_class = Edition

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['editions'] = self.get_editions()
        return context

    @staticmethod
    def get_configuration_codes():
        """
        Filter configurations with at least one edition. Only editions that are 'applied' to the
        database should be listed on the release notes page.
        """
        return Configuration.objects.exclude(
            edition=2015
        ).values(
            'code', 'edition'
        )

    def get_editions(self):
        """
        Get all subclasses of the edition_class ('Edition') that are applied to the database.
        """
        codes = self.get_configuration_codes()
        # See glob pattern: https://pymotw.com/3/glob/
        for module in self.edition_root.glob('[!base][!__init__]*.py'):
            subclass = self.find_subclass(module)
            if {'code': subclass.code, 'edition': str(subclass.edition)} in codes:
                yield subclass

    def find_subclass(self, module: Path) -> Edition:
        """
        Load given module, and return the subclass of self.edition_class
        """
        # https://docs.python.org/3/library/importlib.html#importing-a-source-file-directly
        spec = importlib.util.spec_from_file_location(
            name='configuration.editions', location=str(module), submodule_search_locations=[]
        )
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)

        # Filter dunder attributes, as only Edition subclasses are looked for.
        for name in filter(lambda name: not name.startswith('__'), dir(module)):
            klass = getattr(module, name)
            with contextlib.suppress(TypeError):
                is_not_base = klass is not self.edition_base_class
                is_subclass = issubclass(klass, self.edition_base_class)
                if is_not_base and is_subclass:
                    # Don't pass references to actual models, as they are not used.
                    return klass(key={}, value={}, configuration={}, translation={})

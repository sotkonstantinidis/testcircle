import contextlib
from unittest.mock import MagicMock, patch

from django.core.cache import cache
from django.core.urlresolvers import reverse
from django.test import RequestFactory, override_settings
from django.utils.translation import get_language

from qcat.tests import TestCase
from configuration.models import Configuration
from configuration.cache import get_configuration, get_cached_configuration
from configuration.views import BuildAllCachesView, delete_caches, EditionNotesView


class CacheTest(TestCase):

    fixtures = ['sample_global_key_values.json', 'sample.json']
    locmem = {'default': {'BACKEND': 'django.core.cache.backends.locmem.'
                                     'LocMemCache'}}

    def setUp(self):
        self.factory = RequestFactory()
        # Initially clear cache
        get_cached_configuration.cache_clear()

    def setup_view(self, view, request, *args, **kwargs):
        """
        Mimic ``as_view()``, but returns view instance.
        Use this function to get view instances on which you can run unit tests,
        by testing specific methods.
        """
        view.request = request
        view.args = args
        view.kwargs = kwargs
        return view

    @override_settings(CACHES=locmem, USE_CACHING=True)
    def test_build_cache(self):
        """
        Integration test: check valid cache after call to view.
        """
        request = self.factory.get(reverse('search:build_caches'))
        request._messages = MagicMock()
        view = self.setup_view(BuildAllCachesView(), request)
        view.get(request)
        self.assertIsNotNone(cache.get('sample_2015_{}'.format(get_language())))

    @override_settings(CACHES=locmem, USE_CACHING=True)
    def test_clear_cache(self):
        config = Configuration.objects.all().first()
        get_configuration(code=config.code, edition=config.edition)
        cache_key = '{}_{}_{}'.format(
            config.code, config.edition, get_language())
        self.assertIsNotNone(cache.get(cache_key))
        request = MagicMock()
        request.user.is_superuser = True

        # Missing messages-framework will raise a type error.
        with contextlib.suppress(TypeError):
            delete_caches(request)
            self.assertIsNone(cache.get(cache_key))


class EditionNotesViewTest(TestCase):

    def setUp(self):
        self.valid_edition = MagicMock(code='valid', edition='sub')
        self.invalid_edition = MagicMock(code='invalid', edition='sub')
        self.configs = [
            {'code': 'valid', 'edition': 'sub'},
        ]

    def get_view(self):
        view = self.setup_view(
            view=EditionNotesView(),
            request=RequestFactory().get(reverse('configuration:release_notes'))
        )
        view.get_configuration_codes = lambda : self.configs
        return view

    def test_get_valid_edition(self):
        view = self.get_view()
        with patch.object(view, 'find_subclass') as subclass:
            subclass.return_value = self.valid_edition
            self.assertListEqual(list(view.get_editions()), [self.valid_edition])

    def test_exclude_unapplied_editions(self):
        view = self.get_view()
        with patch.object(view, 'find_subclass') as subclass:
            subclass.return_value = self.invalid_edition
            self.assertEqual(list(view.get_editions()), [])

    def test_find_subclass(self):
        view = self.get_view()

        # Minimal version of an edition
        class Foo(view.edition_base_class):
            code = 'technologies'
            edition = 'sub'

        # Mock a 'module' with the attribute Foo, so it is found by dir(module).
        module = MagicMock()
        module.Foo = Foo

        with patch('configuration.views.importlib.util') as importlib:
            importlib.module_from_spec.return_value = module
            self.assertIsInstance(view.find_subclass(''), Foo)

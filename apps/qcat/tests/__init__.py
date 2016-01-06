from django.test import TestCase as DjangoTestCase
from nose.plugins.attrib import attr
from django.test.utils import override_settings

TEST_CACHES = {
    'default': {
        'BACKEND': 'django.core.cache.backends.filebased.FileBasedCache',
        'LOCATION': '/var/tmp/django_cache/test',
        'TIMEOUT': 0,
    }
}


@override_settings(CACHES=TEST_CACHES)
@override_settings(DEBUG=True)
@override_settings(USE_TZ=False)
@attr('unit')
class TestCase(DjangoTestCase):
    pass

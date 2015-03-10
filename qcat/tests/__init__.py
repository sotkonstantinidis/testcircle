from django.test import TestCase as DjangoTestCase
from nose.plugins.attrib import attr
from django.test.utils import override_settings


@override_settings(DEBUG=True)
@override_settings(USE_TZ=False)
@attr('unit')
class TestCase(DjangoTestCase):
    pass

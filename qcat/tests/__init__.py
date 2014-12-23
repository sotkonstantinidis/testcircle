from django.test import TestCase as DjangoTestCase
from nose.plugins.attrib import attr


@attr('unit')
class TestCase(DjangoTestCase):
    pass

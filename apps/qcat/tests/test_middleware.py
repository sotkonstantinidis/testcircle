from unittest import mock

from django.test import override_settings

from qcat.tests import TestCase
from qcat.middleware import StaffFeatureToggleMiddleware


class MiddlewareTests(TestCase):

    def setUp(self):
        self.middleware = StaffFeatureToggleMiddleware()
        request = mock.MagicMock(META={'REMOTE_ADDR': '0'})
        request.user.is_staff = False
        self.request = request

    def test_normal_user(self):
        self.middleware.process_request(request=self.request)
        self.assertFalse(self.middleware.feature_toggles['is_cde_user'])

    def test_is_staff_user(self):
        self.request.user.is_staff = True
        self.middleware.process_request(request=self.request)
        self.assertTrue(self.middleware.feature_toggles['is_cde_user'])

    @override_settings(CDE_SUBNET_ADDR='1.2.3.')
    def test_is_cde_subnet(self):
        self.request.META['REMOTE_ADDR'] = '1.2.3.4'
        self.middleware.process_request(request=self.request)
        self.assertTrue(self.middleware.feature_toggles['is_cde_user'])

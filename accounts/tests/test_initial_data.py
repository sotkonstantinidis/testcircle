from django.contrib.auth.models import Group, Permission

from qcat.tests import TestCase


class InitialGroupsTest(TestCase):

    fixtures = ['groups_permissions.json']

    def test_all_groups_are_loaded(self):
        self.assertEqual(Group.objects.count(), 2)

    def test_administrators_have_all_permissions(self):
        admin_group = Group.objects.get(name='Administrators')
        self.assertEqual(
            admin_group.permissions.count(), Permission.objects.count())

    def test_translators_have_status_permissions(self):
        translator_group = Group.objects.get(name='Translators')
        self.assertEqual(translator_group.permissions.count(), 3)
        # Only contains permissions with content_type = 8
        self.assertEqual(len(translator_group.permissions.all().exclude(
            content_type=15)), 0)


class InitialPermissionsTest(TestCase):

    def test_all_permissions_are_loaded(self):
        permissions = Permission.objects.count()
        self.assertEqual(permissions, 57)

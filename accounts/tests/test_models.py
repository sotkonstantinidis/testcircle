from django.test import TestCase
from django.contrib.auth import get_user_model

User = get_user_model()


class UserModelTest(TestCase):

    def test_user_is_valid_with_email_only(self):
        user = User(email='a@b.com')
        user.full_clean()  # should not raise

    def test_email_is_primary_key(self):
        user = User()
        self.assertFalse(hasattr(user, 'id'))

    def test_is_authenticated(self):
        user = User()
        self.assertTrue(user.is_authenticated())

    def test_is_active(self):
        user = User()
        self.assertTrue(user.is_active())

    def test_create_new_returns_new_object(self):
        returned = User.create_new(email='a@b.com')
        new_user = User.objects.get(email='a@b.com')
        self.assertEqual(returned, new_user)

    def test_create_new_sets_name(self):
        user = User.create_new(email='a@b.com', name='Foo')
        self.assertEqual(user.name, 'Foo')

    def test_update_updates_name(self):
        user = User.create_new(email='a@b.com', name='Foo')
        user.update(name='Bar')
        self.assertEqual(user.name, 'Bar')

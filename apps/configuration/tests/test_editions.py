from unittest import mock

from configuration.models import Configuration
from qcat.tests import TestCase
from ..editions.base import Edition
from ..editions.technologies_2018 import Technologies


class EditionsTest(TestCase):

    def setUp(self):
        super().setUp()
        self.mock_choices = [('test_code', 'test_code'), ]

    @staticmethod
    def get_edition():
        class TestEdition(Edition):
            code = 'test_code'
            edition = '1234'

        return TestEdition

    def test_invalid_code(self):
        operation = mock.MagicMock(is_operation=True)
        edition = self.get_edition()
        edition.foo = operation
        with self.assertRaises(AttributeError):
            edition()

    @mock.patch.object(Configuration, 'CODE_CHOICES', new_callable=mock.PropertyMock)
    def test_no_operations(self, mock_choices):
        mock_choices.return_value = self.mock_choices
        with self.assertRaises(NotImplementedError):
            ed = self.get_edition()()

    @mock.patch.object(Configuration, 'CODE_CHOICES', new_callable=mock.PropertyMock)
    def test_decorated_operation(self, mock_choices):
        edition = self.get_edition()
        mock_choices.return_value = self.mock_choices
        operation = mock.MagicMock(is_operation=True)
        edition.foo = operation
        no_operation = mock.MagicMock(is_operation=False)
        edition.bar = no_operation

        self.assertEqual(
            edition().operations,
            [operation]
        )

    def test_new_type(self):
        data = {
            "keyword": "some_keyword",
            "configuration": {
                "type": "text"
            }
        }
        expected = {
            "keyword": "some_keyword",
            "configuration": {
                "type": "checkbox"
            },
            "value": [1, 2, 3]
        }
        edition = Technologies
        self.assertDictEqual(
            edition().change_type(**data),
            expected
        )

    @mock.patch.object(Configuration, 'CODE_CHOICES', new_callable=mock.PropertyMock)
    def test_operations_called(self, mock_choices):
        mock_choices.return_value = self.mock_choices
        operation = mock.MagicMock(is_operation=True)
        edition = self.get_edition()
        edition.foo = operation
        edition.save_object = mock.MagicMock()
        edition().run_operations(configuration=mock.MagicMock())
        operation.assert_called_once()

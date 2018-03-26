from unittest import mock

from qcat.tests import TestCase
from ..editions.base import Edition
from ..editions.technologies_2018 import Technologies


class EditionsTest(TestCase):

    def setUp(self):
        super().setUp()
        self.edition = Edition
        self.edition.code = 'technologies'
        self.edition.edition = 'test'

    def test_no_operations(self):
        with self.assertRaises(NotImplementedError):
            self.edition()

    def test_decorated_operation(self):
        # @todo: patch model choices!
        operation = mock.MagicMock(is_operation=True)
        self.edition.foo = operation
        no_operation = mock.MagicMock(is_operation=False)
        self.edition.bar = no_operation
        self.assertEqual(
            self.edition().operations,
            [operation]
        )

    def test_new_type(self):
        data = {
            "keyword": "tech_who_implemented",
            "configuration": {
                "type": "text"
            }
        }
        expected = {
            "keyword": "tech_who_implemented",
            "configuration": {
                "type": "checkbox"
            },
            "value": [1, 2, 3]
        }
        self.edition = Technologies
        self.assertDictEqual(
            self.edition().change_type(**data),
            expected
        )

    def test_operations_called(self):
        operation = mock.MagicMock(is_operation=True)
        self.edition.operations = [operation]
        self.edition.save_object = mock.MagicMock()
        self.edition().run_operations(configuration=mock.MagicMock())
        operation.assert_called_once()

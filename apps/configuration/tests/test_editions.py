from unittest import mock

from qcat.tests import TestCase
from configuration.models import Configuration, Key, Value, Translation
from ..editions.base import Edition


class EditionsTest(TestCase):

    @property
    def model_kwargs(self):
        return dict(
            key=mock.MagicMock(spec=Key),
            value=mock.MagicMock(spec=Value),
            configuration=mock.MagicMock(spec=Configuration),
            translation=mock.MagicMock(spec=Translation)
        )

    def get_edition(self, code='test_code', edition='1234'):

        class TestEdition(Edition):
            def __init__(self, code, edition, **kwargs):
                self.code = code
                self.edition = edition
                super().__init__(**kwargs)

        return TestEdition(
            code=code,
            edition=edition,
            **self.model_kwargs
        )

    def test_invalid_code(self):
        with self.assertRaises(AttributeError):
            self.get_edition()

    @mock.patch.object(Configuration, 'CODE_CHOICES', new_callable=mock.PropertyMock)
    def test_no_operations(self, mock_choices):
        mock_choices.return_value = [('test_code', 'test_code'), ]
        with self.assertRaises(NotImplementedError):
            self.get_edition().operations

    @mock.patch.object(Configuration, 'CODE_CHOICES', new_callable=mock.PropertyMock)
    def test_new_translation(self, mock_choices):
        mock_choices.return_value = [('test_code', 'test_code'), ]

        new_translation = {'label': 'bar'}
        edition = self.get_edition()
        translation_obj = mock.MagicMock()
        edition.translation.objects.get.return_value = translation_obj

        edition.update_translation(
            update_pk=1, **new_translation
        )
        self.assertIn(
            mock.call.data.update({'test_code_1234': new_translation}),
            translation_obj.method_calls
        )

from qcat.tests import TestCase
from qcat.utils import find_dict_in_list


class FindDictInListTest(TestCase):

    def setUp(self):
        self.l = [
            {
                "foo": "bar",
                "bar": "faz"
            }, {
                "foo": "faz"
            }, {
                "faz": "foo"
            }, {
                "foo": "bar"
            }
        ]

    def test_finds_dict(self):
        retu = find_dict_in_list(self.l, 'foo', 'faz')
        self.assertEqual(retu, {"foo": "faz"})

    def test_returns_not_found(self):
        retu = find_dict_in_list(self.l, 'foo', 'foo')
        self.assertEqual(retu, {})

    def test_returns_custom_not_found(self):
        retu = find_dict_in_list(self.l, 'foo', 'foo', not_found="foo")
        self.assertEqual(retu, "foo")

    def test_returns_first_occurence(self):
        retu = find_dict_in_list(self.l, 'foo', 'bar')
        self.assertEqual(retu, {"foo": "bar", "bar": "faz"})

    def test_returns_not_found_if_value_None(self):
        retu = find_dict_in_list(self.l, 'foo', None)
        self.assertEqual(retu, {})

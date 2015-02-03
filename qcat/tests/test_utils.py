from qcat.tests import TestCase
from qcat.utils import (
    find_dict_in_list,
    get_session_questionnaire,
    save_session_questionnaire,
)
from qcat.utils import session_store


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


class GetSessionQuestionnaireTest(TestCase):

    def setUp(self):
        self.session_store = session_store
        self.session_store.clear()

    def test_returns_empty_dict_if_no_session_questionnaire(self):
        ret = get_session_questionnaire()
        self.assertEqual(ret, {})

    def test_returns_empty_dict_if_session_questionnaires_not_list(self):
        self.session_store['session_questionnaires'] = "foo"
        ret = get_session_questionnaire()
        self.assertEqual(ret, {})

    def test_returns_empty_dict_if_session_questionnaire_empty(self):
        self.session_store['session_questionnaires'] = []
        ret = get_session_questionnaire()
        self.assertEqual(ret, {})

    def test_always_returns_first_session_questionnaire(self):
        self.session_store['session_questionnaires'] = [
            {"foo": "bar"}, {"bar": "faz"}]
        ret = get_session_questionnaire()
        self.assertEqual(ret, {"foo": "bar"})


class SaveSessionQuestionnaireTest(TestCase):

    def setUp(self):
        self.session_store = session_store
        self.session_store.clear()

    def test_saves_questionnaire(self):
        self.assertIsNone(self.session_store.get('session_questionnaires'))
        save_session_questionnaire({"foo": "bar"})
        self.assertEqual(
            self.session_store.get('session_questionnaires'), [{"foo": "bar"}])

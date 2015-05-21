from qcat.tests import TestCase
from qcat.utils import (
    clear_session_questionnaire,
    find_dict_in_list,
    is_empty_list_of_dicts,
    get_session_questionnaire,
    save_session_questionnaire,
    session_store,
)


class IsEmptyListOfDictsTest(TestCase):

    def test_returns_false_if_not_empty(self):
        is_empty = is_empty_list_of_dicts([{"foo": "bar"}])
        self.assertFalse(is_empty)

    def test_returns_true_if_empty(self):
        is_empty = is_empty_list_of_dicts([{"foo": ""}])
        self.assertTrue(is_empty)

    def test_returns_true_if_empty_with_None(self):
        is_empty = is_empty_list_of_dicts([{"foo": None}])
        self.assertTrue(is_empty)

    def test_returns_true_if_false_as_value(self):
        is_empty = is_empty_list_of_dicts([{"foo": False}])
        self.assertFalse(is_empty)

    def test_returns_true_if_empty_list(self):
        is_empty = is_empty_list_of_dicts([{"foo": []}])
        self.assertTrue(is_empty)

    def test_returns_False_if_not_empty_in_nested_dict(self):
        is_empty = is_empty_list_of_dicts([{"foo": {"en": "bar"}}])
        self.assertFalse(is_empty)

    def test_returns_true_if_empty_in_nested_dict(self):
        is_empty = is_empty_list_of_dicts([{"foo": {"en": ""}}])
        self.assertTrue(is_empty)

    def test_returns_true_if_None_in_nested_dict(self):
        is_empty = is_empty_list_of_dicts([{"foo": {"en": None}}])
        self.assertTrue(is_empty)

    def test_returns_true_if_false_as_value_in_nested_dict(self):
        is_empty = is_empty_list_of_dicts([{"foo": {"en": False}}])
        self.assertFalse(is_empty)


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
        ret = get_session_questionnaire('sample')
        self.assertEqual(ret, {})

    def test_returns_empty_dict_if_session_questionnaires_not_list(self):
        self.session_store['session_questionnaires'] = "foo"
        ret = get_session_questionnaire('sample')
        self.assertEqual(ret, {})

    def test_returns_empty_dict_if_session_questionnaire_empty(self):
        self.session_store['session_questionnaires'] = []
        ret = get_session_questionnaire('sample')
        self.assertEqual(ret, {})

    def test_returns_correct_session_questionnaire(self):
        self.session_store['session_questionnaires'] = [
            {
                'configuration': 'foo',
                'questionnaire': {'foo': 'bar'}
            }, {
                'configuration': 'sample',
                'questionnaire': {'faz': 'bar'}
            }
        ]
        ret = get_session_questionnaire('sample')
        self.assertEqual(ret, {'faz': 'bar'})


class SaveSessionQuestionnaireTest(TestCase):

    def setUp(self):
        self.session_store = session_store
        self.session_store.clear()

    def test_saves_questionnaire(self):
        self.assertIsNone(self.session_store.get('session_questionnaires'))
        save_session_questionnaire({'foo': 'bar'}, 'sample')
        q = self.session_store.get('session_questionnaires')
        self.assertIsInstance(q, list)
        self.assertEqual(len(q), 1)
        q = q[0]
        self.assertEqual(len(q), 3)
        self.assertEqual(q['questionnaire'], {'foo': 'bar'})
        self.assertEqual(q['configuration'], 'sample')
        self.assertIn('modified', q)

    def test_save_overwrites_existing_questionnaire(self):
        save_session_questionnaire({'foo': 'bar'}, 'sample')
        save_session_questionnaire({'faz': 'bar'}, 'sample')
        q = self.session_store.get('session_questionnaires')
        self.assertIsInstance(q, list)
        self.assertEqual(len(q), 1)
        q = q[0]
        self.assertEqual(len(q), 3)
        self.assertEqual(q['questionnaire'], {'faz': 'bar'})
        self.assertEqual(q['configuration'], 'sample')
        self.assertIn('modified', q)

    def test_save_adds_other_configuration_questionnaire(self):
        save_session_questionnaire({'foo': 'bar'}, 'sample')
        save_session_questionnaire({'faz': 'bar'}, 'foo')
        q = self.session_store.get('session_questionnaires')
        self.assertIsInstance(q, list)
        self.assertEqual(len(q), 2)
        q_1 = q[0]
        self.assertEqual(len(q_1), 3)
        self.assertEqual(q_1['questionnaire'], {'foo': 'bar'})
        self.assertEqual(q_1['configuration'], 'sample')
        q_2 = q[1]
        self.assertEqual(len(q_2), 3)
        self.assertEqual(q_2['questionnaire'], {'faz': 'bar'})
        self.assertEqual(q_2['configuration'], 'foo')


class ClearSessionQuestionnaireTest(TestCase):

    def setUp(self):
        self.session_store = session_store
        self.session_store.clear()

    def test_clears_questionnaire(self):
        self.session_store['session_questionnaires'] = 'foo'
        clear_session_questionnaire()
        self.assertEqual(self.session_store['session_questionnaires'], [])

    def test_only_clears_questionnaire(self):
        self.session_store['foo'] = 'bar'
        clear_session_questionnaire()
        self.assertEqual(self.session_store['foo'], 'bar')

    def test_clears_questionnaire_by_configuration_code(self):
        self.session_store['session_questionnaires'] = [
            {
                'configuration': 'foo',
                'questionnaire': {'foo': 'bar'}
            }, {
                'configuration': 'sample',
                'questionnaire': {'faz': 'bar'}
            }
        ]
        clear_session_questionnaire(configuration_code='sample')
        q = self.session_store['session_questionnaires']
        self.assertEqual(len(q), 1)
        q = q[0]
        self.assertEqual(q['questionnaire'], {'foo': 'bar'})
        self.assertEqual(q['configuration'], 'foo')

    def test_passes_if_questionnaire_by_code_not_found(self):
        self.session_store['session_questionnaires'] = [
            {
                'configuration': 'foo',
                'questionnaire': {'foo': 'bar'}
            }, {
                'configuration': 'sample',
                'questionnaire': {'faz': 'bar'}
            }
        ]
        clear_session_questionnaire(configuration_code='faz')
        q = self.session_store['session_questionnaires']
        self.assertEqual(len(q), 2)

    def test_passes_if_session_store_empty(self):
        clear_session_questionnaire(configuration_code='')  # Should not raise

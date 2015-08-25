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
        ret = get_session_questionnaire('sample', 'code')
        self.assertEqual(ret, {})

    def test_returns_empty_dict_if_session_questionnaires_not_dict(self):
        self.session_store['session_questionnaires'] = "foo"
        ret = get_session_questionnaire('sample', 'code')
        self.assertEqual(ret, {})

    def test_returns_empty_dict_if_session_questionnaire_empty(self):
        self.session_store['session_questionnaires'] = {}
        ret = get_session_questionnaire('sample', 'code')
        self.assertEqual(ret, {})

    def test_returns_correct_session_questionnaire(self):
        self.session_store['session_questionnaires'] = {
            'foo': [
                {
                    'code': 'code_1',
                    'questionnaire': {'foo': 'bar'},
                }, {
                    'code': 'code_2',
                    'questionnaire': {'asdf': 'bar'},
                }
            ],
            'sample': [
                {
                    'code': 'code_1',
                    'questionnaire': {'faz': 'bar'},
                }
            ]
        }
        ret = get_session_questionnaire('sample', 'code_1')
        self.assertEqual(
            ret, {'code': 'code_1', 'questionnaire': {'faz': 'bar'}})

    def test_returns_new_if_no_questionnaire_code(self):
        self.session_store['session_questionnaires'] = {
            'foo': [
                {
                    'code': 'code_1',
                    'questionnaire': {'foo': 'bar'},
                }, {
                    'code': 'new',
                    'questionnaire': {'asdf': 'bar'},
                }
            ],
            'sample': [
                {
                    'code': 'code_1',
                    'questionnaire': {'faz': 'bar'},
                }
            ]
        }
        ret = get_session_questionnaire('foo', None)
        self.assertEqual(
            ret, {'code': 'new', 'questionnaire': {'asdf': 'bar'}})

    def test_returns_first_occurence_if_multiple_questionnaires(self):
        self.session_store['session_questionnaires'] = {
            'foo': [
                {
                    'code': 'code_1',
                    'questionnaire': {'foo': 'bar'},
                }, {
                    'code': 'code_1',
                    'questionnaire': {'asdf': 'bar'},
                }
            ],
            'sample': [
                {
                    'code': 'code_1',
                    'questionnaire': {'faz': 'bar'},
                }
            ]
        }
        ret = get_session_questionnaire('foo', 'code_1')
        self.assertEqual(
            ret, {'code': 'code_1', 'questionnaire': {'foo': 'bar'}})

    def test_returns_empty_dict_if_configuration_not_found(self):
        self.session_store['session_questionnaires'] = {
            'foo': [
                {
                    'code': 'code_1',
                    'questionnaire': {'foo': 'bar'},
                }, {
                    'code': 'code_2',
                    'questionnaire': {'asdf': 'bar'},
                }
            ],
            'sample': [
                {
                    'code': 'code_1',
                    'questionnaire': {'faz': 'bar'},
                }
            ]
        }
        ret = get_session_questionnaire('faz', 'code_1')
        self.assertEqual(ret, {})

    def test_returns_empty_dict_if_questionnaire_not_found(self):
        self.session_store['session_questionnaires'] = {
            'foo': [
                {
                    'code': 'code_1',
                    'questionnaire': {'foo': 'bar'},
                }, {
                    'code': 'code_2',
                    'questionnaire': {'asdf': 'bar'},
                }
            ],
            'sample': [
                {
                    'code': 'code_1',
                    'questionnaire': {'faz': 'bar'},
                }
            ]
        }
        ret = get_session_questionnaire('foo', 'code')
        self.assertEqual(ret, {})


class SaveSessionQuestionnaireTest(TestCase):

    def setUp(self):
        self.session_store = session_store
        self.session_store.clear()

    def test_saves_questionnaire(self):
        self.assertIsNone(self.session_store.get('session_questionnaires'))
        save_session_questionnaire(
            'sample', 'code', {'data': 'bar'}, {'links': 'bar'})
        q = self.session_store.get('session_questionnaires')
        self.assertIsInstance(q, dict)
        self.assertEqual(len(q), 1)
        self.assertIn('sample', q)
        q = q['sample']
        self.assertIsInstance(q, list)
        self.assertEqual(len(q), 1)
        q = q[0]
        self.assertEqual(len(q), 4)
        self.assertEqual(q['questionnaire'], {'data': 'bar'})
        self.assertEqual(q['links'], {'links': 'bar'})
        self.assertEqual(q['code'], 'code')
        self.assertIn('modified', q)

    def test_save_questionnaire_with_no_questionnaire_code(self):
        self.assertIsNone(self.session_store.get('session_questionnaires'))
        save_session_questionnaire(
            'sample', None, {'data': 'bar'}, {'links': 'bar'})
        q = self.session_store.get('session_questionnaires')
        self.assertIsInstance(q, dict)
        self.assertEqual(len(q), 1)
        self.assertIn('sample', q)
        q = q['sample']
        self.assertIsInstance(q, list)
        self.assertEqual(len(q), 1)
        q = q[0]
        self.assertEqual(len(q), 4)
        self.assertEqual(q['questionnaire'], {'data': 'bar'})
        self.assertEqual(q['links'], {'links': 'bar'})
        self.assertEqual(q['code'], 'new')
        self.assertIn('modified', q)

    def test_save_overwrites_existing_questionnaire(self):
        save_session_questionnaire(
            'sample', 'code', {'data': 'foo'}, {'links': 'foo'})
        save_session_questionnaire(
            'sample', 'code', {'data': 'bar'}, {'links': 'bar'})
        q = self.session_store.get('session_questionnaires')
        self.assertIsInstance(q, dict)
        self.assertEqual(len(q), 1)
        self.assertIn('sample', q)
        q = q['sample']
        self.assertIsInstance(q, list)
        self.assertEqual(len(q), 1)
        q = q[0]
        self.assertEqual(len(q), 4)
        self.assertEqual(q['questionnaire'], {'data': 'bar'})
        self.assertEqual(q['links'], {'links': 'bar'})
        self.assertEqual(q['code'], 'code')
        self.assertIn('modified', q)

    def test_save_adds_same_configuration_questionnaire(self):
        save_session_questionnaire(
            'sample', 'code_1', {'data': 'foo'}, {'links': 'foo'})
        save_session_questionnaire(
            'sample', 'code_2', {'data': 'bar'}, {'links': 'bar'})
        q = self.session_store.get('session_questionnaires')
        self.assertIsInstance(q, dict)
        self.assertEqual(len(q), 1)
        self.assertIn('sample', q)
        q = q['sample']
        self.assertIsInstance(q, list)
        self.assertEqual(len(q), 2)
        q_1 = q[0]
        self.assertEqual(len(q_1), 4)
        self.assertEqual(q_1['questionnaire'], {'data': 'foo'})
        self.assertEqual(q_1['links'], {'links': 'foo'})
        self.assertEqual(q_1['code'], 'code_1')
        self.assertIn('modified', q_1)
        q_2 = q[1]
        self.assertEqual(len(q_2), 4)
        self.assertEqual(q_2['questionnaire'], {'data': 'bar'})
        self.assertEqual(q_2['links'], {'links': 'bar'})
        self.assertEqual(q_2['code'], 'code_2')
        self.assertIn('modified', q_2)

    def test_save_adds_other_configuration_questionnaire(self):
        save_session_questionnaire(
            'sample', 'code', {'data': 'foo'}, {'links': 'foo'})
        save_session_questionnaire(
            'foo', 'code', {'data': 'bar'}, {'links': 'bar'})
        q = self.session_store.get('session_questionnaires')
        self.assertIsInstance(q, dict)
        self.assertEqual(len(q), 2)
        self.assertIn('sample', q)
        self.assertIn('foo', q)
        q_sample = q['sample']
        self.assertIsInstance(q_sample, list)
        self.assertEqual(len(q_sample), 1)
        q_1 = q_sample[0]
        self.assertEqual(len(q_1), 4)
        self.assertEqual(q_1['questionnaire'], {'data': 'foo'})
        self.assertEqual(q_1['links'], {'links': 'foo'})
        self.assertEqual(q_1['code'], 'code')
        q_foo = q['foo']
        self.assertIsInstance(q_foo, list)
        self.assertEqual(len(q_foo), 1)
        q_2 = q_foo[0]
        self.assertEqual(len(q_2), 4)
        self.assertEqual(q_2['questionnaire'], {'data': 'bar'})
        self.assertEqual(q_2['links'], {'links': 'bar'})
        self.assertEqual(q_2['code'], 'code')


class ClearSessionQuestionnaireTest(TestCase):

    def setUp(self):
        self.session_store = session_store
        self.session_store.clear()

    def test_clears_questionnaire(self):
        self.session_store['session_questionnaires'] = 'foo'
        clear_session_questionnaire()
        self.assertEqual(self.session_store['session_questionnaires'], {})

    def test_only_clears_questionnaire(self):
        self.session_store['foo'] = 'bar'
        clear_session_questionnaire()
        self.assertEqual(self.session_store['foo'], 'bar')

    def test_clears_questionnaire_by_configuration_code(self):
        self.session_store['session_questionnaires'] = {
            'foo': [
                {
                    'questionnaire': {'foo': 'bar'},
                }
            ],
            'sample': [
                {
                    'questionnaire': {'faz': 'bar'},
                }
            ]
        }
        clear_session_questionnaire(configuration_code='sample')
        q = self.session_store['session_questionnaires']
        self.assertEqual(len(q), 1)
        self.assertNotIn('sample', q)
        self.assertIn('foo', q)
        q = q['foo']
        self.assertIsInstance(q, list)
        self.assertEqual(len(q), 1)
        q = q[0]
        self.assertEqual(q['questionnaire'], {'foo': 'bar'})

    def test_clears_questionnaire_by_questionnaire_code(self):
        self.session_store['session_questionnaires'] = {
            'foo': [
                {
                    'code': 'code_1',
                    'questionnaire': {'foo': 'bar'},
                }, {
                    'code': 'code_2',
                    'questionnaire': {'asdf': 'bar'},
                }
            ],
            'sample': [
                {
                    'code': 'code_1',
                    'questionnaire': {'faz': 'bar'},
                }
            ]
        }
        clear_session_questionnaire(
            configuration_code='foo', questionnaire_code='code_1')
        q = self.session_store['session_questionnaires']
        self.assertEqual(len(q), 2)
        q_foo = q['foo']
        self.assertIsInstance(q_foo, list)
        self.assertEqual(len(q_foo), 1)
        self.assertEqual(q_foo[0]['questionnaire'], {'asdf': 'bar'})
        self.assertEqual(q_foo[0]['code'], 'code_2')
        q_sample = q['sample']
        self.assertIsInstance(q_sample, list)
        self.assertEqual(len(q_sample), 1)
        self.assertEqual(q_sample[0]['questionnaire'], {'faz': 'bar'})
        self.assertEqual(q_sample[0]['code'], 'code_1')

    def test_passes_if_questionnaire_by_code_not_found(self):
        initial = {
            'foo': [
                {
                    'questionnaire': {'foo': 'bar'},
                }
            ],
            'sample': [
                {
                    'questionnaire': {'faz': 'bar'},
                }
            ]
        }
        self.session_store['session_questionnaires'] = initial
        clear_session_questionnaire(configuration_code='faz')
        q = self.session_store['session_questionnaires']
        self.assertEqual(q, initial)

    def test_passes_if_questionnaire_code_not_found(self):
        initial = {
            'foo': [
                {
                    'code': 'code_1',
                    'questionnaire': {'foo': 'bar'},
                }
            ]
        }
        self.session_store['session_questionnaires'] = initial
        clear_session_questionnaire(
            configuration_code='foo', questionnaire_code='code_2')
        q = self.session_store['session_questionnaires']
        self.assertEqual(q, initial)

    def test_passes_if_session_store_empty(self):
        clear_session_questionnaire(configuration_code='')  # Should not raise

from qcat.tests import TestCase
from questionnaire.templatetags.list_to_columns import columnize


def get_list_of_elements():
    return [1, 2, 3, 4, 5, 6, 7, 8, 9, 10]


class ColumnizeTest(TestCase):

    def test_returns_columns_times_list(self):
        cols = columnize(get_list_of_elements(), 2)
        self.assertEqual(len(cols), 2)
        cols = columnize(get_list_of_elements(), 5)
        self.assertEqual(len(cols), 5)
        cols = columnize(get_list_of_elements(), 11)
        self.assertEqual(len(cols), 11)

    def test_uneven_divisions_are_filled_up_front(self):
        cols = columnize(get_list_of_elements(), 3)
        self.assertEqual(len(cols[0]), 4)
        self.assertEqual(len(cols[1]), 3)
        self.assertEqual(len(cols[2]), 3)

from .base import Edition, operation


class Technologies(Edition):
    """
    Questionnaire updates for carbon benefit.
    """
    type = 'technologies'
    edition = 2018

    @operation
    def country_as_checkbox(self):
        return {
            'diff': '',
            'question_keyword': 'path to the question in the current structure? is this relevant?',
            'help_text': 'Unstructured text is now a list of given options'
        }

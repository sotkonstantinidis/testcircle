from .base import Edition, Operation


class Technologies(Edition):
    """
    Questionnaire updates for carbon benefit.
    """
    code = 'technologies'
    edition = 2018

    @property
    def change_type(self) -> Operation:
        return Operation(
            transformation=self.change_question_type,
            release_note=''
        )

    def change_question_type(self, **data):
        return data

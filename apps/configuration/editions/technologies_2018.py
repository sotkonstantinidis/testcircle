from .base import Edition, operation


class Technologies(Edition):
    """
    Questionnaire updates for carbon benefit.
    """
    code = 'technologies'
    edition = 2018

    @operation
    def change_type(self, **data) -> dict:
        return data

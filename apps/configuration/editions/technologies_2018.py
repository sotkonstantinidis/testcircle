from .base import Edition, Operation


class Technologies(Edition):
    """
    Questionnaire updates for carbon benefit.
    """
    code = 'technologies'
    edition = 2018

    @property
    def operations(self):
        return [
            Operation(
                transformation=self.rename_tech_lu_grazingland_pastoralism,
                release_note=''
            )
        ]

    def rename_tech_lu_grazingland_pastoralism(self, **data) -> dict:
        self.update_translation(
            update_pk=1759,
            **{
                'label': {
                    'en': 'Semi-nomadic pastoralism'
                },
                'helptext': {
                    'en': '<strong>Semi-nomadic pastoralism</strong>: animal owners have a permanent place of residence where supplementary cultivation is practiced. Herds are moved to distant grazing grounds.'
                }
            }
        )
        return data

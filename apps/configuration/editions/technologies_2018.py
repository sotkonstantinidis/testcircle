from .base import Edition, Operation


class Technologies(Edition):
    """
    Questionnaire updates for carbon benefit.
    """
    code = 'technologies'
    edition = 2018

    @property
    def rename_tech_lu_grazingland_pastoralism(self) -> Operation:
        return Operation(
            transformation=self.change_question_type,
            release_note=''
        )

    def change_question_type(self, **data):
        new_translation = self.translation.objects.create(translation_type='value', data={
            'technologies': {
                'label': {
                    'en': 'Semi-nomadic pastoralism'
                },
                "helptext": {
                    "en": "<strong>Semi-nomadic pastoralism</strong>: animal owners have a permanent place of residence where supplementary cultivation is practiced. Herds are moved to distant grazing grounds."
                }
            }
        })
        value = self.value.objects.get(pk=1259)
        value.translation = new_translation
        value.save()
        return data

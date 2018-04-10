from django.utils.translation import ugettext_lazy as _

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
                release_note=_('x.x: Rename label')
            ),
            Operation(
                transformation=self.add_tech_lu_initial,
                release_note=_('3.2: Added new question about initial land use')
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

    def add_tech_lu_initial(self, **data) -> dict:
        qg_path = ('section_specifications', 'tech__3', 'tech__3__2', 'tech_qg_7')
        qg_data = self.find_in_data(path=qg_path, **data)

        self.create_new_question(
            keyword='tech_lu_initial',
            translation={
                'label': {
                    'en': 'Initial land use'
                }
            },
            question_type='select',
            values=[
                self.create_new_value(
                    keyword='tech_lu_initial_1',
                    translation={
                        'label': {
                            'en': 'Land use 1'
                        }
                    }
                ),
                self.create_new_value(
                    keyword='tech_lu_initial_2',
                    translation={
                        'label': {
                            'en': 'Land use 2'
                        }
                    }
                ),
            ])

        qg_data['questions'] = [{'keyword': 'tech_lu_initial'}] + qg_data['questions']
        data = self.update_data(path=qg_path, updated=qg_data, **data)
        return data

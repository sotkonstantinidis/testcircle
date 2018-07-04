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
                transform_configuration=self.rename_tech_lu_grazingland_pastoralism,
                release_note=_('3.2: Renamed option "semi-nomadism" of land use type "Grazing land" to "semi-nomadic pastoralism".')
            ),
            Operation(
                transform_configuration=self.add_option_tech_lu_grazingland_transhumant,
                release_note=_('3.2: Added option "transhumant pastoralism" to land use type "Grazing land".')
            ),
            Operation(
                transform_configuration=self.add_option_tech_lu_mixed_integrated,
                release_note=_('3.2: Added option "integrated crop-livestock" to land use type "Mixed".')
            ),
            Operation(
                transform_configuration=self.add_tech_lu_initial,
                release_note=_('3.2: Added new question "Initial land use".')
            ),
            Operation(
                transform_configuration=self.remove_tech_est_type,
                transform_questionnaire=self.delete_tech_est_type,
                release_note=_('4.4: Removed "Type of measure" from Establishment activities.')
            ),
            Operation(
                transform_configuration=self.remove_tech_maint_type,
                transform_questionnaire=self.delete_tech_maint_type,
                release_note=_('4.6: Removed "Type of measure" from Maintenance activities.')
            ),
            Operation(
                transform_configuration=self.move_tech_input_est_total_estimation,
                release_note='',
            ),
            Operation(
                transform_configuration=self.rename_tech_input_est_total_estimation,
                release_note='',
            ),
            Operation(
                transform_configuration=self.move_tech_input_maint_total_estimation,
                release_note='',
            ),
            Operation(
                transform_configuration=self.rename_tech_input_maint_total_estimation,
                release_note='',
            ),
            Operation(
                transform_configuration=self.rename_tech_individuals,
                release_note='',
            )
        ]

    def rename_tech_individuals(self, **data) -> dict:
        # Add option to show helptext as tooltip. Then add tooltip.
        qg_path = (
            'section_specifications', 'tech__5', 'tech__5__6', 'tech_qg_71')
        qg_data = self.find_in_data(path=qg_path, **data)
        questions = []
        for question in qg_data['questions']:
            if question['keyword'] == 'tech_individuals':
                question['form_options'] = {'helptext_position': 'tooltip'}
            questions.append(question)
        qg_data['questions'] = questions
        data = self.update_config_data(path=qg_path, updated=qg_data, **data)
        self.update_translation(
            update_pk=1139,
            **{
                'label': {
                    'en': 'Individuals or groups'
                },
                'helptext': {
                    'en': 'Indicate if land users apply the technology as individuals or as members of a specific group/ company.'
                }
            }
        )
        return data

    def rename_tech_input_maint_total_estimation(self, **data) -> dict:
        self.update_translation(
            update_pk=1321,
            **{
                'label': {
                    'en': 'If you are unable to break down the costs, give an estimation of the total costs of maintaining the Technology'
                }
            }
        )
        return data

    def move_tech_input_maint_total_estimation(self, **data) -> dict:
        qg_path = (
            'section_specifications', 'tech__4', 'tech__4__7', 'tech_qg_50')
        qg_data = self.find_in_data(path=qg_path, **data)
        del qg_data['form_options']
        del qg_data['view_options']
        data = self.update_config_data(path=qg_path, updated=qg_data, **data)
        return data

    def rename_tech_input_est_total_estimation(self, **data) -> dict:
        self.update_translation(
            update_pk=1319,
            **{
                'label': {
                    'en': 'If you are unable to break down the costs, give an estimation of the total costs of establishing the Technology'
                }
            }
        )
        return data

    def move_tech_input_est_total_estimation(self, **data) -> dict:
        qg_path = (
            'section_specifications', 'tech__4', 'tech__4__5', 'tech_qg_42')
        qg_data = self.find_in_data(path=qg_path, **data)
        del qg_data['form_options']
        del qg_data['view_options']
        data = self.update_config_data(path=qg_path, updated=qg_data, **data)
        return data

    def remove_tech_maint_type(self, **data) -> dict:
        qg_path = (
            'section_specifications', 'tech__4', 'tech__4__6', 'tech_qg_43')
        qg_data = self.find_in_data(path=qg_path, **data)
        qg_data['questions'] = [
            q for q in qg_data['questions'] if q['keyword'] != 'tech_maint_type']
        data = self.update_config_data(path=qg_path, updated=qg_data, **data)
        return data

    def delete_tech_maint_type(self, **data) -> dict:
        return self.update_data('tech_qg_43', 'tech_maint_type', None, **data)

    def remove_tech_est_type(self, **data) -> dict:
        qg_path = (
            'section_specifications', 'tech__4', 'tech__4__4', 'tech_qg_165')
        qg_data = self.find_in_data(path=qg_path, **data)
        qg_data['questions'] = [
            q for q in qg_data['questions'] if q['keyword'] != 'tech_est_type']
        data = self.update_config_data(path=qg_path, updated=qg_data, **data)
        return data

    def delete_tech_est_type(self, **data: dict) -> dict:
        return self.update_data('tech_qg_165', 'tech_est_type', None, **data)

    def add_option_tech_lu_mixed_integrated(self, **data) -> dict:
        self.add_new_value(
            question_keyword='tech_lu_mixed_sub',
            value=self.create_new_value(
                keyword='lu_mixed_integrated',
                translation={
                    'label': {
                        'en': 'Agro-pastoralism, integrated crop-livestock'
                    }
                },
                order_value=2
            ),
            order_value=2
        )
        return data

    def add_option_tech_lu_grazingland_transhumant(self, **data) -> dict:
        self.add_new_value(
            question_keyword='tech_lu_grazingland_extensive',
            value=self.create_new_value(
                keyword='lu_grazingland_transhumant',
                translation={
                    'label': {
                        'en': 'Transhumant pastoralism'
                    }
                },
                order_value=4
            ),
        )
        return data

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
                self.get_value('tech_lu_cropland'),
                self.get_value('tech_lu_grazingland'),
                self.get_value('tech_lu_forest'),
                self.get_value('tech_lu_mixed'),
                self.get_value('tech_lu_settlements'),
                self.get_value('tech_lu_waterways'),
                self.get_value('tech_lu_mines'),
                self.get_value('tech_lu_unproductive'),
            ])

        qg_data['questions'] = [{'keyword': 'tech_lu_initial'}] + qg_data['questions']
        data = self.update_config_data(path=qg_path, updated=qg_data, **data)
        return data

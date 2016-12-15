import logging

from django.conf import settings
from configuration.configuration import QuestionnaireQuestion
from configuration.configured_questionnaire import ConfiguredQuestionnaire
from .models import Questionnaire
from .templatetags.questionnaire_tags import get_static_map_url

logger = logging.getLogger(__name__)


class ConfiguredQuestionnaireSummary(ConfiguredQuestionnaire):
    """
    Get only data which is configured to appear in the summary. This is defined
    by the configuration-field: 'in_summary', which specifies the section
    of the summary for given field for the chosen summary-config (e.g. 'full',
    'one page', 'four page').
    """

    def __init__(self, config, summary_type: str,
                 questionnaire: Questionnaire, **data):
        self.summary_type = summary_type
        self.data = {}
        super().__init__(questionnaire=questionnaire, config=config, **data)

    def put_question_data(self, child: QuestionnaireQuestion):
        """
        Put the value to self.data, using the name as defined in the config
        ('in_summary': {'this_type': <key_name>}}.
        As some key names are duplicated by virtue (config may use the same
        question twice), but represent different and important content, some
        keys are overridden with the help of the questions questiongroup.

        This cannot be solved on the config as the same question is listed
        twice, so the key-name overriding setting must be ready for versioning.
        """
        if child.in_summary and child.in_summary.get(self.summary_type):
            field_name = child.in_summary[self.summary_type]
            qg_field = '{questiongroup}.{field}'.format(
                questiongroup=child.questiongroup.keyword,
                field=field_name
            )
            override = settings.CONFIGURATION_SUMMARY_OVERRIDE.get(qg_field, {})
            field_name = override.get('override_key', field_name)
            get_value_fn = override.get(
                'override_fn', lambda self, child: self.get_value(child)
            )

            if field_name not in self.data:
                self.data[field_name] = get_value_fn(self, child)
            else:
                # This can be intentional, e.g. header_image is a list. In this
                # case, only the first element is available.
                logger.warn(
                    'The field {key} for the summary {summary_type} is defined '
                    'more than once'.format(
                        key=child.in_summary[self.summary_type],
                        summary_type=self.summary_type
                    )
                )

    def get_map_values(self, child: QuestionnaireQuestion):
        """
        Configured function (see ConfigurationConf) for special preparation of
        data to display map data.
        """
        if not self.questionnaire.geom:
            return {'img_url': '', 'coordinates': ''}
        else:
            return {
                'img_url': get_static_map_url(self.questionnaire),
                'coordinates': self.questionnaire.geom.coords
            }

    def get_full_range_values(self, child: QuestionnaireQuestion):
        values = self.values.get(child.parent_object.keyword)
        if not values:
            return {}
        if len(values) != 1:
            raise NotImplementedError()
        selected = values[0].get(child.keyword)
        for choice in child.choices:
            yield {'highlighted': choice[0] in selected, 'text': choice[1]}

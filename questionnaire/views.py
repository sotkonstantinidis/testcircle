from django.contrib.formtools.wizard.views import NamedUrlSessionWizardView
from django.http import Http404
from django.shortcuts import render, redirect

from questionnaire.config.base import BaseConfig
from questionnaire.models import Questionnaire


class QuestionnaireWizard(NamedUrlSessionWizardView):

    template_name = 'questionnaire.html'

    def done(self, form_list, form_dict, **kwargs):

        baseConfig = BaseConfig()

        baseDict = {}
        for step, stepData in form_dict.items():
            baseDict[baseConfig.getConfigByStep(step)] = stepData.cleaned_data
        json = {'base': baseDict}

        return redirect(Questionnaire.create_new(json=json))


def questionnaire_view(request, questionnaire_id):
    try:
        questionnaire = Questionnaire.objects.get(id=questionnaire_id)
    except Questionnaire.DoesNotExist:
        raise Http404
    return render(request, 'questionnaire_view.html', {
        'questionnaire': questionnaire})

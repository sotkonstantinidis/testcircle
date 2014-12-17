from django.contrib import messages
from django.contrib.formtools.wizard.views import NamedUrlSessionWizardView
from django.http import Http404
from django.shortcuts import render, redirect
from django.utils.translation import ugettext as _

from questionnaire.config.base import BaseConfig
from questionnaire.models import Questionnaire

from configuration.configuration import read_configuration


class QuestionnaireWizard(NamedUrlSessionWizardView):

    template_name = 'questionnaire.html'

    def done(self, form_list, form_dict, **kwargs):

        baseConfig = BaseConfig()

        baseDict = {}
        for step, stepData in form_dict.items():
            baseDict[baseConfig.getConfigByStep(step)] = stepData.cleaned_data
        json = {'base': baseDict}
        questionnaire = Questionnaire.create_new(data=json)
        messages.success(
            self.request, _('The questionnaire was successfully submitted.'))
        return redirect(questionnaire)


def questionnaire_view(request, questionnaire_id):
    try:
        questionnaire = Questionnaire.objects.get(id=questionnaire_id)
    except Questionnaire.DoesNotExist:
        raise Http404
    return render(request, 'questionnaire_view.html', {
        'questionnaire': questionnaire})


def questionnaire_new(request):
    category = read_configuration()

    formsets = []
    for subcategory in category.subcategories:
        for questionset in subcategory.questionsets:
            form = questionset.get_form(request.POST or None)
            if request.method == 'POST':
                print ("=====")
                print (questionset.keyword)
                print (form.cleaned_data)
                print (form.is_valid())
                print ("=====")
            formsets.append(('Label', form))

    return render(request, 'questionnaire_new.html', {'formsets': formsets})

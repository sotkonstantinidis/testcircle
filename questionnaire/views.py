from django.http import HttpResponseRedirect
from django.contrib.formtools.wizard.views import NamedUrlSessionWizardView


class QuestionnaireWizard(NamedUrlSessionWizardView):

    template_name = 'questionnaire.html'

    def done(self, form_list, form_dict, **kwargs):

        print ("****")
        print (form_list)
        x = [form.cleaned_data for form in form_list]
        print (x)
        print (form_dict)

        return HttpResponseRedirect('/')

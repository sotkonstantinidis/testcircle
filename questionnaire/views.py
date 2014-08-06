from django.http import HttpResponseRedirect
from django.contrib.formtools.wizard.views import SessionWizardView


class QuestionnaireWizard(SessionWizardView):

    template_name = 'questionnaire.html'

    def done(self, form_list, form_dict, **kwargs):

        print ("****")
        print (form_list)
        x = [form.cleaned_data for form in form_list]
        print (x)
        print (form_dict)

        do_something_with_the_form_data(form_list)
        return HttpResponseRedirect('/page-to-redirect-to-when-done/')

from django.http import Http404
from django.shortcuts import render, redirect
from django.contrib import messages

from configuration.configuration import QuestionnaireConfiguration


def home(request):

    # TODO: Show this warning here? Or in Admin?
    questionnaire_configuration = QuestionnaireConfiguration('unccd')
    if questionnaire_configuration.configuration_error is not None:
        messages.error(
            request, 'WARNING: INVALID CONFIGURATION. {}'.format(
                questionnaire_configuration.configuration_error))

    return render(request, 'unccd/home.html')


def questionnaire_new_step(request, step):

    questionnaire_configuration = QuestionnaireConfiguration('unccd')
    category = questionnaire_configuration.get_category(step)

    if category is None:
        raise Http404

    initial_data = {}
    if request.method != 'POST':
        initial_data = request.session.get('session_questionnaire', {})

    category_config, category_formsets = category.get_form(
        request.POST or None, initial_data=initial_data)

    if request.method == 'POST':
        valid = True
        data = {}
        for __, subcategory_formsets in category_formsets:
            for formset in subcategory_formsets:

                valid = valid and formset.is_valid()

                if valid is False:
                    break

                for f in formset.forms:
                    questiongroup_keyword = f.prefix.split('-')[0]
                    try:
                        data[questiongroup_keyword].append(f.cleaned_data)
                    except KeyError:
                        data[questiongroup_keyword] = [f.cleaned_data]

        if valid is True:
            session_data = request.session.get('session_questionnaire', {})
            session_data.update(data)
            request.session['session_questionnaire'] = session_data
            messages.success(
                request, '[TODO] Data successfully stored to Session.')
            return redirect('unccd_questionnaire_new')

    return render(request, 'unccd/questionnaire/new_step.html', {
        'category_formsets': category_formsets,
        'category_config': category_config
    })


def questionnaire_new(request):

    # request.session.clear()

    questionnaire_configuration = QuestionnaireConfiguration('unccd')

    # data = {
    #     "qg_1": [
    #         {
    #             "key_1": "Foo",
    #             "key_3": "Bar",
    #         }
    #     ]
    # }
    data = request.session.get('session_questionnaire', {})
    if data != {}:
        messages.info(request, '[TODO] Data retrieved from Session.')

    categories = questionnaire_configuration.render_readonly_form(data)

    return render(request, 'unccd/questionnaire/new.html', {
        'categories': categories
    })

from django.shortcuts import render
from django.http import Http404

from configuration.configuration import QuestionnaireConfiguration

questionnaire_configuration = QuestionnaireConfiguration('unccd')


def home(request):
    return render(request, 'unccd/home.html')


def questionnaire_new_step(request, step):

    category = questionnaire_configuration.get_category(step)

    if category is None:
        raise Http404

    category_config, category_formsets = category.get_form(
        request.POST or None)

    if request.method == 'POST':
        for __, subcategory_formsets in category_formsets:
            for formset in subcategory_formsets:
                print (formset.is_valid())

                for f in formset:
                    print ("****")
                    print (f)
                    print (f.prefix)
                    print (f.cleaned_data)

    return render(request, 'unccd/questionnaire/new_step.html', {
        'category_formsets': category_formsets,
        'category_config': category_config
    })


def questionnaire_new(request):

    data = {
        "qg_1": [
            {
                "key_1": "Foo",
                "key_3": "Bar",
            }
        ]
    }

    categories = questionnaire_configuration.render_readonly_form(data)

    return render(request, 'unccd/questionnaire/new.html', {
        'categories': categories
    })

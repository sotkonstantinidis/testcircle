from django.shortcuts import render

from configuration.configuration import read_configuration


def home(request):
    return render(request, 'unccd/home.html')


def questionnaire_new(request):
    category = read_configuration('unccd')

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

    return render(
        request, 'unccd/questionnaire/new_step.html', {
            'category_formsets': category_formsets,
            'category_config': category_config
        })

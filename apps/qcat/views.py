from django.contrib import sitemaps
from django.core.urlresolvers import reverse_lazy
from django.shortcuts import render
from django.utils.decorators import method_decorator
from django.views.decorators.cache import cache_page
from django.views.generic import TemplateView


def home(request):
    return render(request, 'home.html')


def about(request):
    return render(request, 'about.html')


class StaticViewSitemap(sitemaps.Sitemap):
    """
    Until a better solution is required: just use a static sitemap.
    """
    def items(self):
        return [
            'wocat:home',
            'technologies:home',
            'approaches:home',
            'login',
        ]

    def location(self, item):
        return reverse_lazy(item)


# Use this for the urls.
static_sitemap = {
    'static': StaticViewSitemap,
}


class FactsTeaserView(TemplateView):
    """
    Display some relevant numbers.
    """
    http_method_names = ['get']
    template_name = 'qcat/templates/fact_sheet_teaser.html'

    @method_decorator(cache_page(5))
    def dispatch(self, request, *args, **kwargs):
        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        """
        Request piwik-api here to protect auth token.
        """
        context = super().get_context_data(**kwargs)
        return context

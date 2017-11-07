import contextlib
import logging

from os.path import join, isfile

from django.conf import settings
from django.db.models import Q
from django.http import Http404
from django.template.response import TemplateResponse
from django.utils.translation import get_language
import bs4

from wkhtmltopdf.views import PDFTemplateView, PDFTemplateResponse

from configuration.cache import get_configuration
from questionnaire.models import Questionnaire
from questionnaire.utils import get_query_status_filter, \
    get_questionnaire_data_in_single_language

from .renderers import TechnologyFullSummaryRenderer, \
    ApproachesFullSummaryRenderer

logger = logging.getLogger(__name__)


class CachedPDFTemplateResponse(PDFTemplateResponse):
    """
    Creating the pdf includes two resource-heavy processes:
    - extracting the json to markup (frontend)
    - call to wkhtmltopdf (backend)

    Therefore, the content is created only once per filename (which should
    distinguish between new questionnaire edits). This only works with
    reasonably precise file names!
    """
    @property
    def file_path(self):
        return join(settings.SUMMARY_PDF_PATH, self.filename)

    def get_rendered_content(self):
        return super().rendered_content

    def content_with_file_cache(self):
        if isfile(self.file_path):
            # Catch any exception, worst case is that the pdf is created from
            # scratch again
            with contextlib.suppress(Exception) as e:
                return open(self.file_path, 'rb').read()

        content = self.get_rendered_content()
        with contextlib.suppress(Exception) as e:
            open(self.file_path, 'wb').write(content)
        return content

    @property
    def rendered_content(self):
        return self.content_with_file_cache()


class DocTemplateResponse(TemplateResponse):
    """
    Create HTML with the default template response, cast the markup to a table. 
    """

    def rows_to_tr(self):
        """
        Prepend a row with 12 elements, forcing 'proper' width of following rows
        """
        for row in self.soup.select('.row'):
            table = self.soup.new_tag('table')
            table.attrs['width'] = '100%'
            row.wrap(table)
            grid_12_columns = '<tr>'
            for i in range(0, 12):
                grid_12_columns += '<td width="8.3%"></td>'
            grid_12_columns += '</tr>'
            row.insert_before(bs4.BeautifulSoup(grid_12_columns, 'lxml'))
            if 'range' not in row.attrs['class']:
                row.unwrap()

    def columns_to_td(self):
        """
        Use columns-width as colspan.
        """
        for column in self.soup.select('.columns'):
            column.name = 'td'

            for i, class_name in enumerate(column.attrs['class']):
                if class_name.startswith('small'):
                    column.attrs['colspan'] = class_name[6:]
                    del column.attrs['class'][i]

    def highlight_list_to_bold(self):
        """
        CSS highlights can not be seen in word, make them bold.
        """
        for highlight in self.soup.select('.highlights_list > .true'):
            highlight.wrap(self.soup.new_tag('strong'))

    def range_to_table(self):
        """
        Cast the 'ranges' to a more basic format.
        """
        for row in self.soup.select('.range'):
            pass

    def html_to_table(self, html: str) -> str:
        """
        Cast the 'fluid' markup to a table so the word-document looks
        as expected by the researchers.
        """
        self.soup = bs4.BeautifulSoup(html, 'lxml')
        css = self.soup.find('link')
        # Cache busting is only done with respect to 'summary.css', so in case
        # changes on the summary_raw.css are made, also change a blank in
        # 'summary.css'.
        css.attrs['href'] = css.attrs['href'].replace(
            'summary.css', 'summary_raw.css'
        )
        self.highlight_list_to_bold()
        self.range_to_table()
        self.columns_to_td()
        self.rows_to_tr()
        return str(self.soup)

    @property
    def rendered_content(self):
        return self.html_to_table(super().rendered_content)


class SummaryPDFCreateView(PDFTemplateView):
    """
    Put the questionnaire data to the context and return the rendered pdf.
    """
    response_class = CachedPDFTemplateResponse
    doc_response_class = DocTemplateResponse
    summary_type = 'full'  # Only one summary type is available right now
    base_template_path = 'summary/'
    http_method_names = ['get']
    render_classes = {
        'technologies': {'full': TechnologyFullSummaryRenderer},
        'approaches': {'full': ApproachesFullSummaryRenderer}
    }
    footer_template = '{}layout/footer.html'.format(base_template_path)
    # see: http://wkhtmltopdf.org/usage/wkhtmltopdf.txt
    cmd_options = {
        'dpi': '96',
        'margin-top': '1cm',
        'margin-bottom': '1cm',
    }
    default_quality = 'screen'

    def get(self, request, *args, **kwargs):
        self.questionnaire = self.get_object(questionnaire_id=self.kwargs['id'])
        try:
            self.code = self.questionnaire.configurations.filter(
                active=True
            ).first().code
        except AttributeError:
            raise Http404
        self.config = get_configuration(configuration_code=self.code)
        self.quality = self.request.GET.get('quality', self.default_quality)
        # filename is set withing render_to_response, this is too late as it's
        # used for caching.
        self.filename = self.get_filename()
        if self.is_doc_file:
            self.response_class = self.doc_response_class
        return super().get(request, *args, **kwargs)

    def get_template_names(self):
        template = self.request.GET.get('template', self.code)
        return '{}/layout/{}.html'.format(self.base_template_path, template)

    def get_filename(self) -> str:
        """
        The filename is specific enough to be used as 'pseudo cache-key' in the
        CachedPDFTemplateResponse.
        """
        return 'wocat-{identifier}-{language}-{summary_type}-{quality}-' \
               'summary-{update}.pdf'.format(
            identifier=self.questionnaire.id,
            language=get_language(),
            summary_type=self.summary_type,
            quality=self.quality,
            update=self.questionnaire.updated.strftime('%Y-%m-%d-%H-%M')
        )

    @property
    def is_doc_file(self):
        return self.request.GET.get('as', '') == 'doc'

    def get_object(self, questionnaire_id: int) -> Questionnaire:
        """
        Get questionnaire and check status / permissions.
        """
        status_filter = get_query_status_filter(self.request)
        status_filter &= Q(id=questionnaire_id)
        obj = Questionnaire.with_status.not_deleted().filter(
            Q(id=questionnaire_id), status_filter
        ).distinct()
        if not obj.exists() or obj.count() != 1:
            raise Http404
        return obj.first()

    def get_summary_data(self, **data):
        """
        Get summary data from renderer according to configuration.
        """
        try:
            renderer = self.render_classes[self.config.keyword][self.summary_type]
        except KeyError:
            raise Http404
        return renderer(
            config=self.config,
            questionnaire=self.questionnaire,
            quality=self.quality,
            base_url=self.request.build_absolute_uri('/'), **data
        ).data

    def get_prepared_data(self, questionnaire: Questionnaire) -> dict:
        """
        Load the prepared JSON for given object in the current language.
        """
        data = get_questionnaire_data_in_single_language(
            questionnaire_data=questionnaire.data,
            locale=get_language(),
            original_locale=questionnaire.original_locale
        )
        return self.get_summary_data(**data)

    def get_footer_context(self) -> dict:
        """
        Provide variables used in the footer template.
        """
        name = self.questionnaire.get_name()
        if len(name) > 70:
            name = '{}...'.format(name[:67])
        return {
            'footer_name': name,
            'footer_config': self.code.title()
        }

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['block'] = self.get_prepared_data(self.questionnaire)
        context.update(self.get_footer_context())
        # For languages with no spaces between words (e.g. Lao, Khmer), add CSS
        # line break rule if either the questionnaire or its original version is
        # in one of these languages.
        if self.questionnaire.original_locale in settings.WORD_WRAP_LANGUAGES \
                or self.request.LANGUAGE_CODE in settings.WORD_WRAP_LANGUAGES:
            context['break_words'] = True
        return context

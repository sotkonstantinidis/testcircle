import functools
import hashlib

from django.apps import AppConfig
from django.contrib.staticfiles import finders


class SummaryConfig(AppConfig):
    name = 'summary'

    def ready(self):
        self.css_file_hash = self.get_css_hash()

    def get_css_hash(self):
        """
        Manual cache-busting for summary css, as wkhtmltopdf only works with full
        urls, but django-compressor only works with files in COMPRESS_URLS. Create
        the file-hash only once: at application start.
        """
        summary_css_path = finders.find('css/summary.css')
        with open(summary_css_path, 'rb') as f:
            d = hashlib.md5()
            for buf in iter(functools.partial(f.read, 128), b''):
                d.update(buf)
        return d.hexdigest()

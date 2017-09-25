from os.path import join

import requests

from accounts.client import WocatWebsiteUserClient
from configuration.models import Institution, Country
from django.core.cache import cache
from django.core.management.base import NoArgsCommand

from configuration.conf import settings


class Command(NoArgsCommand, WocatWebsiteUserClient):

    created = []
    updated = []
    deleted = []

    def handle_noargs(self, **options):

        institutions = self.fetch_institutions()

        for institution in institutions:
            self.create_or_update_institutions(institution)

        self.delete_institutions()

        self.update_cache()

        self.stdout.write(
            f'Created {len(self.created)} institutions, '
            f'updated {len(self.updated)} institutions, '
            f'deleted (set inactive) {len(self.deleted)} institutions')

    def delete_institutions(self):
        active_ids = self.created + self.updated
        self.deleted = Institution.objects.exclude(id__in=active_ids)
        self.deleted.update(active=False)

    def create_or_update_institutions(self, institution: dict):

        # Prepare DB values
        values = {
            'id': int(institution['id']),
            'name': institution['name'],
            'abbreviation': institution['abbreviation'],
            'country': Country.get(institution['country']),
            'active': True,
            'url': institution['url'],
            'external_url': institution['external_url'],
            'logo': self.get_logo_file(institution['logo']),
        }

        institution_object, created = Institution.objects.update_or_create(
            id=values['id'], defaults=values
        )

        if created is True:
            self.created.append(institution_object.id)
        else:
            self.updated.append(institution_object.id)

    def fetch_institutions(self):
        api_end_point = 'institutions/'

        r = self._get(api_end_point)

        if r.ok:
            return r.json()

        else:
            self.stdout.write(
                f'Error syncing institutions: '
                f'Query to API returned status {r.status_code}')
            return []

    def get_logo_file(self, url: str) -> str:
        """
        Call given url, store it as a file and return the file name.
        """
        if not url:
            return ''

        response = self.get_request_logo(url)
        if not response:
            return ''

        return self.write_to_file(response)

    def get_request_logo(self, url: str):
        response = requests.get(url)
        return None if not response.ok else response

    def write_to_file(self, response) -> str:
        """
        Write the responses content to a file, and return its name.
        """
        request_file_name = response.url.split('/')[-1]
        file_name = join(settings.MEDIA_ROOT, 'institutions', request_file_name)
        with open(file_name, 'wb') as f:
            f.write(response.content)
        return file_name.replace(settings.MEDIA_ROOT, '.')

    @staticmethod
    def update_cache():
        # Update happens on first call of Institution.as_select()
        for language in settings.LANGUAGES:
            cache_key = '{key}-{language}'.format(
                key=settings.CONFIGURATION_CACHE_KEY_INSTITUTION_SELECT,
                language=language[0]
            )
            cache.delete(cache_key)

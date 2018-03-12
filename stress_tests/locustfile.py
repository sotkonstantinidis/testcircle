import random

from locust import HttpLocust, TaskSet, task


class UserBehavior(TaskSet):
    """
    Typical tasks that users perform.
    This should also touch all included components (db, elasticsearch, login api).
    """
    def on_start(self):
        # maybe: use environment variables
        self.approaches = ['approaches_490']
        self.technologies = ['technologies_784']
        self.user_id = 3088
        self.languages = ['en', 'fr', 'es', 'ru', 'km', 'lo', 'ar', 'pt', 'af']

    @property
    def language(self):
        return '/{language}'.format(language=random.choice(self.languages))

    @task(2)
    def start_edit(self):
        """
        Check the configuration and lru_cache
        """
        self.client.get('{}/wocat/technologies/edit/new/'.format(self.language))

    @task(10)
    def index(self):
        self.client.get('/')

    @task(20)
    def index_list(self):
        self.client.get('{}/wocat/list/'.format(self.language))

    @task(3)
    def user_profile(self):
        """
        Check the db
        """
        self.client.get('{}/accounts/user/{}/'.format(self.language, self.user_id))

    @task(5)
    def approach(self):
        """
        Check cache, db (initial request)
        """
        self.client.get('{}/wocat/approaches/view/{}'.format(self.language, random.choice(self.approaches)))

    @task(5)
    def technology(self):
        """
        Check cache, db (initial request)
        """
        self.client.get('{}/wocat/approaches/view/{}'.format(self.language, random.choice(self.technologies)))


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 2000
    max_wait = 5000

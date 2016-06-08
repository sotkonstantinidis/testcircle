import random

from locust import HttpLocust, TaskSet, task


class UserBehavior(TaskSet):
    """
    Typical tasks that users perform.
    This should also touch all included components (db, elasticsearch, login api).
    """
    def on_start(self):
        # maybe: use environment variables
        self.approaches = []
        self.technologies = []
        self.user_id = 0
        self.credentials = {}

    @task(1)
    def login(self):
        """
        Check the login, incl. the 'API'
        """
        response = self.client.get('/en/accounts/login/')
        credentials = self.credentials
        credentials['csrfmiddlewaretoken'] = response.cookies['csrftoken']
        self.client.headers['Referer'] = self.client.base_url
        self.client.post('/en/accounts/login/', credentials)

    @task(2)
    def start_edit(self):
        """
        Check the configuration and lru_cache
        """
        self.login()
        self.client.get('/en/wocat/technologies/edit/new/')

    @task(10)
    def index(self):
        self.client.get('/')

    @task(3)
    def my_slm_data(self):
        """
        Check the db
        """
        self.login()
        self.client.get('/en/accounts/user/{}/questionnaires/'.format(self.user_id))

    @task(5)
    def approach(self):
        """
        Check cache, db (initial request)
        """
        self.client.get('/en/wocat/approaches/view/approaches_{}'.format(random.choice(self.approaches)))

    @task(5)
    def technology(self):
        """
        Check cache, db (initial request)
        """
        self.client.get('/en/wocat/approaches/view/technologies_{}'.format(random.choice(self.technologies)))


class WebsiteUser(HttpLocust):
    task_set = UserBehavior
    min_wait = 2000
    max_wait = 5000

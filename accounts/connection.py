import MySQLdb
from django.conf import settings


def get_connection():
    """
    When specifying multiple databases in the settings the normal way, Django
    tries to create each database when running the tests. As the authentication
    database has readonly access, this is not possible.

    This function returns a database connection based on the settings named
    AUTH_DATABASE.
    """

    try:
        connection_settings = settings.AUTH_DATABASE
    except AttributeError:
        raise Exception(
            'No database connection for authentication specified in settings! '
            'Please specify AUTH_DATABASE.')

    if connection_settings['ENGINE'] != 'django.db.backends.mysql':
        raise Exception(
            'The authentication database must be a MySQL database!')

    return MySQLdb.connect(
        host=connection_settings['HOST'],
        port=connection_settings['PORT'],
        user=connection_settings['USER'],
        passwd=connection_settings['PASSWORD'],
        db=connection_settings['NAME']
    )

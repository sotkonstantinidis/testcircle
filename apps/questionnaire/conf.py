from django.conf import settings  # noqa
from appconf import AppConf


class QuestionnaireConf(AppConf):
    """
    Verbose names for statuses and roles
    """
    # Status list
    DRAFT = 1
    SUBMITTED = 2
    REVIEWED = 3
    PUBLIC = 4
    REJECTED = 5
    INACTIVE = 6
    # Roles
    COMPILER = 'compiler'
    EDITOR = 'editor'
    REVIEWER = 'reviewer'
    PUBLISHER = 'publisher'
    SECRETARIAT = 'secretariat'
    LANDUSER = 'landuser'
    RESOURCEPERSON = 'resourceperson'
    FLAGGER = 'flagger'

    FLAG_UNCCD = 'unccd_bp'

    METADATA_KEYS = [
        'created',
        'updated',
        'compilers',
        'editors',
        'code',
        'configurations',
        'translations',
        'status',
        'flags',
    ]

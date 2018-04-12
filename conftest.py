"""
Use this file to setup envdir and django-configurations, as this works nicely with PyCharms
integrated (clickable) test feature.
"""

import os
import envdir
import configurations

envdir.read(os.path.join(os.path.dirname(__file__), 'envs'))
configurations.setup()

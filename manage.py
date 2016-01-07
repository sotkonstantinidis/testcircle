#!/usr/bin/env python
import sys
from os.path import join, dirname

import envdir as envdir

if __name__ == "__main__":
    # Load the environment variables in the folder ``./envs/`` with *envdir*.
    envdir.read(join(dirname(__file__), 'envs'))

    # Please note that this is *django-configurations* and not *Django*.
    from configurations.management import execute_from_command_line

    execute_from_command_line(sys.argv)

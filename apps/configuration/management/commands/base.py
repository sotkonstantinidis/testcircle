# -*- coding: utf-8 -*-
import subprocess

from django.core.management.base import NoArgsCommand
from django.utils.translation import ugettext_lazy as _


class DevelopNoArgsCommand(NoArgsCommand):
    """
    This command can be executed on the 'develop' branch only.
    """

    def handle_noargs(self, **options):
        git_branch = subprocess.check_output(
            ['git', 'symbolic-ref', '--short', '-q', 'HEAD'],
            stderr=subprocess.STDOUT
        )
        if git_branch != b'develop\n':
            raise Exception(_(u"This command can only be exectured on the "
                              u"'develop' branch. See the docs for more info."))

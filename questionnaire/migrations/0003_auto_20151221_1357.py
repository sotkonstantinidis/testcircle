# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('questionnaire', '0002_questionnaire_data_old'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='questionnaire',
            options={'permissions': (('review_questionnaire', 'Can review questionnaire'), ('publish_questionnaire', 'Can publish questionnaire')), 'ordering': ['-updated']},
        ),
        migrations.AlterField(
            model_name='questionnairemembership',
            name='role',
            field=models.CharField(max_length=64, choices=[('compiler', 'Compiler'), ('editor', 'Editor'), ('reviewer', 'Reviewer'), ('publisher', 'Publisher'), ('landuser', 'Land User')]),
            preserve_default=True,
        ),
    ]

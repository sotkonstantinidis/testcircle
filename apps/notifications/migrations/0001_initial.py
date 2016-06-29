# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('questionnaire', '0010_questionnaire_is_deleted'),
    ]

    operations = [
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('action', models.PositiveIntegerField(choices=[(1, 'created questionnaire'), (2, 'deleted questionnaire'), (3, 'changed status'), (4, 'added member'), (5, 'removed member')])),
                ('status', models.PositiveIntegerField(blank=True, null=True, choices=[(1, 'Draft'), (2, 'Submitted'), (3, 'Reviewed'), (4, 'Public'), (5, 'Rejected'), (6, 'Inactive')])),
                ('message', models.TextField()),
                ('questionnaire', models.ForeignKey(to='questionnaire.Questionnaire')),
                ('receivers', models.ManyToManyField(related_name='receivers', to=settings.AUTH_USER_MODEL)),
                ('sender', models.ForeignKey(related_name='sender', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
    ]

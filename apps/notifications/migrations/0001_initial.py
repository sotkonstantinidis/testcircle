# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_pgjson.fields
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('questionnaire', '0011_merge'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ContentUpdate',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('data', django_pgjson.fields.JsonBField()),
            ],
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('action', models.PositiveIntegerField(choices=[(1, 'created questionnaire'), (2, 'deleted questionnaire'), (3, 'changed status'), (4, 'added member'), (5, 'removed member'), (6, 'edited content')])),
                ('catalyst', models.ForeignKey(to=settings.AUTH_USER_MODEL, help_text='Person triggering the log', related_name='catalyst')),
                ('questionnaire', models.ForeignKey(to='questionnaire.Questionnaire')),
                ('subscribers', models.ManyToManyField(to=settings.AUTH_USER_MODEL, help_text='All people that are members of the questionnaire', related_name='subscribers')),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='StatusUpdate',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('status', models.PositiveIntegerField(choices=[(1, 'Draft'), (2, 'Submitted'), (3, 'Reviewed'), (4, 'Public'), (5, 'Rejected'), (6, 'Inactive')], blank=True, null=True)),
                ('message', models.TextField()),
                ('log', models.OneToOneField(to='notifications.Log')),
            ],
        ),
        migrations.AddField(
            model_name='contentupdate',
            name='log',
            field=models.OneToOneField(to='notifications.Log'),
        ),
    ]

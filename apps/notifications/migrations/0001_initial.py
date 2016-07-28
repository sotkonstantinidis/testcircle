# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
from django.conf import settings
import django_pgjson.fields


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('questionnaire', '0011_merge'),
    ]

    operations = [
        migrations.CreateModel(
            name='ContentUpdate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('data', django_pgjson.fields.JsonBField()),
            ],
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('action', models.PositiveIntegerField(choices=[(1, 'created questionnaire'), (2, 'deleted questionnaire'), (3, 'changed status'), (4, 'invited'), (5, 'removed'), (6, 'edited content')])),
                ('catalyst', models.ForeignKey(help_text='Person triggering the log', related_name='catalyst', to=settings.AUTH_USER_MODEL)),
                ('questionnaire', models.ForeignKey(to='questionnaire.Questionnaire')),
                ('subscribers', models.ManyToManyField(related_name='subscribers', help_text='All people that are members of the questionnaire', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='MemberUpdate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('role', models.CharField(max_length=50)),
                ('affected', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('log', models.OneToOneField(to='notifications.Log')),
            ],
        ),
        migrations.CreateModel(
            name='StatusUpdate',
            fields=[
                ('id', models.AutoField(verbose_name='ID', serialize=False, auto_created=True, primary_key=True)),
                ('status', models.PositiveIntegerField(null=True, blank=True, choices=[(1, 'Draft'), (2, 'Submitted'), (3, 'Reviewed'), (4, 'Public'), (5, 'Rejected'), (6, 'Inactive')])),
                ('log', models.OneToOneField(to='notifications.Log')),
            ],
        ),
        migrations.AddField(
            model_name='contentupdate',
            name='log',
            field=models.OneToOneField(to='notifications.Log'),
        ),
    ]

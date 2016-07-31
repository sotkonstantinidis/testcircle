# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import django_pgjson.fields
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('questionnaire', '0011_merge'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='ContentUpdate',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('data', django_pgjson.fields.JsonBField()),
            ],
        ),
        migrations.CreateModel(
            name='Log',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('action', models.PositiveIntegerField(choices=[(1, 'created questionnaire'), (2, 'deleted questionnaire'), (3, 'changed status'), (4, 'invited'), (5, 'removed'), (6, 'edited content')])),
                ('catalyst', models.ForeignKey(to=settings.AUTH_USER_MODEL, related_name='catalyst', help_text='Person triggering the log')),
                ('questionnaire', models.ForeignKey(to='questionnaire.Questionnaire')),
                ('subscribers', models.ManyToManyField(to=settings.AUTH_USER_MODEL, help_text='All people that are members of the questionnaire', related_name='subscribers')),
            ],
            options={
                'ordering': ['-created'],
            },
        ),
        migrations.CreateModel(
            name='MemberUpdate',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('role', models.CharField(max_length=50)),
                ('affected', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
                ('log', models.OneToOneField(to='notifications.Log')),
            ],
        ),
        migrations.CreateModel(
            name='ReadLog',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('is_read', models.BooleanField(default=False)),
                ('log', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to='notifications.Log')),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.PROTECT, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.CreateModel(
            name='StatusUpdate',
            fields=[
                ('id', models.AutoField(serialize=False, primary_key=True, verbose_name='ID', auto_created=True)),
                ('status', models.PositiveIntegerField(blank=True, choices=[(1, 'Draft'), (2, 'Submitted'), (3, 'Reviewed'), (4, 'Public'), (5, 'Rejected'), (6, 'Inactive')], null=True)),
                ('log', models.OneToOneField(to='notifications.Log')),
            ],
        ),
        migrations.AddField(
            model_name='contentupdate',
            name='log',
            field=models.OneToOneField(to='notifications.Log'),
        ),
        migrations.AlterUniqueTogether(
            name='readlog',
            unique_together=set([('log', 'user')]),
        ),
    ]

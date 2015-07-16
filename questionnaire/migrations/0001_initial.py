# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_pgjson.fields
import uuid
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('configuration', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('uuid', models.CharField(max_length=64)),
                ('uploaded', models.DateTimeField(auto_now=True)),
                ('content_type', models.CharField(max_length=64)),
                ('size', models.BigIntegerField(null=True)),
                ('thumbnails', django_pgjson.fields.JsonBField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Questionnaire',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('data', django_pgjson.fields.JsonBField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('uuid', models.CharField(default=uuid.uuid4, max_length=64)),
                ('code', models.CharField(default='', max_length=64)),
                ('blocked', models.BooleanField(default=False)),
                ('status', models.IntegerField(choices=[(1, 'Draft'), (2, 'Pending'), (3, 'Published'), (4, 'Rejected'), (5, 'Inactive')])),
                ('version', models.IntegerField()),
            ],
            options={
                'permissions': (('can_moderate', 'Can moderate'),),
                'ordering': ['-updated'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='QuestionnaireConfiguration',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('original_configuration', models.BooleanField(default=False)),
                ('configuration', models.ForeignKey(to='configuration.Configuration')),
                ('questionnaire', models.ForeignKey(to='questionnaire.Questionnaire')),
            ],
            options={
                'ordering': ['-original_configuration'],
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='QuestionnaireLink',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('from_status', models.IntegerField(choices=[(1, 'Draft'), (2, 'Pending'), (3, 'Published'), (4, 'Rejected'), (5, 'Inactive')])),
                ('to_status', models.IntegerField(choices=[(1, 'Draft'), (2, 'Pending'), (3, 'Published'), (4, 'Rejected'), (5, 'Inactive')])),
                ('from_questionnaire', models.ForeignKey(related_name='from_questionnaire', to='questionnaire.Questionnaire')),
                ('to_questionnaire', models.ForeignKey(related_name='to_questionnaire', to='questionnaire.Questionnaire')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='QuestionnaireMembership',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('role', models.CharField(choices=[('author', 'Author'), ('editor', 'Editor')], max_length=64)),
                ('questionnaire', models.ForeignKey(to='questionnaire.Questionnaire')),
                ('user', models.ForeignKey(to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='QuestionnaireTranslation',
            fields=[
                ('id', models.AutoField(verbose_name='ID', primary_key=True, auto_created=True, serialize=False)),
                ('language', models.CharField(choices=[('en', 'English'), ('es', 'Spanish')], max_length=63)),
                ('original_language', models.BooleanField(default=False)),
                ('questionnaire', models.ForeignKey(to='questionnaire.Questionnaire')),
            ],
            options={
                'ordering': ['-original_language'],
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='questionnaire',
            name='configurations',
            field=models.ManyToManyField(through='questionnaire.QuestionnaireConfiguration', to='configuration.Configuration'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='questionnaire',
            name='links',
            field=models.ManyToManyField(through='questionnaire.QuestionnaireLink', to='questionnaire.Questionnaire', related_name='linked_to+', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='questionnaire',
            name='members',
            field=models.ManyToManyField(through='questionnaire.QuestionnaireMembership', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]

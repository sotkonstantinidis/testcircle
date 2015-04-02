# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_pgjson.fields
import uuid
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('configuration', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='File',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
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
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('data', django_pgjson.fields.JsonBField()),
                ('created', models.DateTimeField(auto_now_add=True)),
                ('updated', models.DateTimeField(auto_now=True)),
                ('uuid', models.CharField(default=uuid.uuid4, max_length=64)),
                ('blocked', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='QuestionnaireMembership',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('questionnaire', models.ForeignKey(to='questionnaire.Questionnaire')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='QuestionnaireRole',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('keyword', models.CharField(max_length=63, unique=True)),
                ('description', models.TextField(null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='QuestionnaireTranslation',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('language', models.CharField(choices=[('en', 'English'), ('es', 'Spanish')], max_length=63)),
                ('original_language', models.BooleanField(default=False)),
                ('questionnaire', models.ForeignKey(to='questionnaire.Questionnaire')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='QuestionnaireVersion',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('data', django_pgjson.fields.JsonBField()),
                ('created', models.DateTimeField(auto_now=True)),
                ('version', models.IntegerField()),
                ('questionnaire', models.ForeignKey(to='questionnaire.Questionnaire')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Status',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('keyword', models.CharField(max_length=63, unique=True)),
                ('description', models.TextField(null=True)),
            ],
            options={
                'verbose_name_plural': 'statuses',
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='questionnaireversion',
            name='status',
            field=models.ForeignKey(to='questionnaire.Status'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='questionnaireversion',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='questionnairemembership',
            name='role',
            field=models.ForeignKey(to='questionnaire.QuestionnaireRole'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='questionnairemembership',
            name='user',
            field=models.ForeignKey(to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='questionnaire',
            name='active',
            field=models.ForeignKey(to='questionnaire.QuestionnaireVersion', related_name='active_questionnaire', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='questionnaire',
            name='configurations',
            field=models.ManyToManyField(to='configuration.Configuration'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='questionnaire',
            name='members',
            field=models.ManyToManyField(through='questionnaire.QuestionnaireMembership', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]

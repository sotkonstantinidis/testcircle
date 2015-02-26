# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import uuid
import django_pgjson.fields


class Migration(migrations.Migration):

    dependencies = [
        ('configuration', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Questionnaire',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('data', django_pgjson.fields.JsonBField()),
                ('created', models.DateTimeField(auto_now=True)),
                ('uuid', models.CharField(max_length=64, default=uuid.uuid4)),
                ('blocked', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='QuestionnaireMembership',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('questionnaire', models.ForeignKey(to='questionnaire.Questionnaire')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='QuestionnaireRole',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('keyword', models.CharField(unique=True, max_length=63)),
                ('description', models.TextField(null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='QuestionnaireTranslation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, verbose_name='ID', serialize=False)),
                ('keyword', models.CharField(unique=True, max_length=63)),
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
            field=models.ForeignKey(null=True, to='questionnaire.QuestionnaireVersion', related_name='active_questionnaire'),
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
            field=models.ManyToManyField(to=settings.AUTH_USER_MODEL, through='questionnaire.QuestionnaireMembership'),
            preserve_default=True,
        ),
    ]

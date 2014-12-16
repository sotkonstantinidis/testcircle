# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django_pgjson.fields


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Category',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('keyword', models.CharField(max_length=63, unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Configuration',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('data', django_pgjson.fields.JsonBField()),
                ('code', models.CharField(max_length=63)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(null=True)),
                ('created', models.DateTimeField(auto_now=True)),
                ('activated', models.DateTimeField(null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Key',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('keyword', models.CharField(max_length=63, unique=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Translation',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('translation_type', models.CharField(max_length=63)),
                ('data', django_pgjson.fields.JsonBField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Value',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('keyword', models.CharField(max_length=63, unique=True)),
                ('translation', models.ForeignKey(to='configuration.Translation')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='key',
            name='translation',
            field=models.ForeignKey(to='configuration.Translation'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='category',
            name='translation',
            field=models.ForeignKey(to='configuration.Translation'),
            preserve_default=True,
        ),
    ]

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
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('keyword', models.CharField(unique=True, max_length=63)),
            ],
            options={
                'verbose_name_plural': 'categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Configuration',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('data', django_pgjson.fields.JsonBField(help_text='\n            The JSON configuration. See section "Questionnaire\n            Configuration" of the manual for more information.<br/>\n            <strong style="color:red;">Warning!</strong> You should not\n            edit existing JSON configurations directly. Instead, create\n            a new version and edit there.<br/><strong>Hint</strong>: Use\n            <a href="https://jqplay.org/">jq play</a> to format your\n            JSON.')),
                ('code', models.CharField(max_length=63, help_text='\n            The internal code of the configuration, e.g. "core", "wocat"\n            or "unccd". The same code can be used multiple times but\n            only one configuration per code can be "active".')),
                ('base_code', models.CharField(blank=True, help_text='\n            The code of the base configuration from which the\n            configuration inherits. An active configuration with the\n            given code needs to exist.', max_length=63)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(blank=True, null=True)),
                ('created', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(help_text='\n            <strong style="color:red;">Warning!</strong> Only one\n            configuration per code can be active. If you set this\n            configuration "active", an existing configuration with the\n            same code will be set inactive.', default=False)),
                ('activated', models.DateTimeField(blank=True, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Key',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('keyword', models.CharField(unique=True, max_length=63)),
                ('data', django_pgjson.fields.JsonBField(help_text='\n            The JSON configuration. See section "Questionnaire\n            Configuration" of the manual for more information.<br/>\n            <strong>Hint</strong>: Use <a href="https://jqplay.org/">jq\n            play</a> to format your JSON.')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Translation',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
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
                ('id', models.AutoField(primary_key=True, verbose_name='ID', auto_created=True, serialize=False)),
                ('keyword', models.CharField(unique=True, max_length=63)),
                ('key', models.ForeignKey(to='configuration.Key')),
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

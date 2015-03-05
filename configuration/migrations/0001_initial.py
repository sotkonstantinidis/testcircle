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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('keyword', models.CharField(max_length=63, unique=True)),
            ],
            options={
                'verbose_name_plural': 'categories',
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Configuration',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('data', django_pgjson.fields.JsonBField(help_text='\n            The JSON configuration. See section "Questionnaire\n            Configuration" of the manual for more information.<br/>\n            <strong style="color:red;">Warning!</strong> You should not\n            edit existing JSON configurations directly. Instead, create\n            a new version and edit there.<br/><strong>Hint</strong>: Use\n            <a href="https://jqplay.org/">jq play</a> to format your\n            JSON.')),
                ('code', models.CharField(help_text='\n            The internal code of the configuration, e.g. "core", "wocat"\n            or "unccd". The same code can be used multiple times but\n            only one configuration per code can be "active".', max_length=63)),
                ('base_code', models.CharField(blank=True, help_text='\n            The code of the base configuration from which the\n            configuration inherits. An active configuration with the\n            given code needs to exist.', max_length=63)),
                ('name', models.CharField(max_length=255)),
                ('description', models.TextField(null=True, blank=True)),
                ('created', models.DateTimeField(auto_now=True)),
                ('active', models.BooleanField(help_text='\n            <strong style="color:red;">Warning!</strong> Only one\n            configuration per code can be active. If you set this\n            configuration "active", an existing configuration with the\n            same code will be set inactive.', default=False)),
                ('activated', models.DateTimeField(null=True, blank=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Key',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('keyword', models.CharField(max_length=63, unique=True)),
                ('configuration', django_pgjson.fields.JsonBField(help_text='\n            The JSON configuration. See section "Questionnaire\n            Configuration" of the manual for more information.<br/>\n            <strong>Hint</strong>: Use <a href="https://jqplay.org/">jq\n            play</a> to format your JSON.')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Questiongroup',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('keyword', models.CharField(max_length=63, unique=True)),
                ('configuration', django_pgjson.fields.JsonBField(blank=True, help_text='\n            The JSON configuration. See section "Questionnaire\n            Configuration" of the manual for more information.<br/>\n            <strong>Hint</strong>: Use <a href="https://jqplay.org/">jq\n            play</a> to format your JSON.')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Translation',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
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
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('keyword', models.CharField(max_length=63, unique=True)),
                ('configuration', django_pgjson.fields.JsonBField(blank=True, help_text='\n            The JSON configuration. See section "Questionnaire\n            Configuration" of the manual for more information.<br/>\n            <strong>Hint</strong>: Use <a href="https://jqplay.org/">jq\n            play</a> to format your JSON.')),
                ('translation', models.ForeignKey(to='configuration.Translation')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='questiongroup',
            name='translation',
            field=models.ForeignKey(null=True, blank=True, to='configuration.Translation'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='key',
            name='translation',
            field=models.ForeignKey(to='configuration.Translation'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='key',
            name='values',
            field=models.ManyToManyField(related_name='keys', to='configuration.Value'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='category',
            name='translation',
            field=models.ForeignKey(to='configuration.Translation'),
            preserve_default=True,
        ),
    ]

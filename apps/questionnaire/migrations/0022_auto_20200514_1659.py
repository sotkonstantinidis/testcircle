# -*- coding: utf-8 -*-
# Generated by Django 1.11.26 on 2020-05-14 14:59
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('questionnaire', '0021_auto_20181011_1340'),
    ]

    operations = [
        migrations.CreateModel(
            name='APIEditRequests',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('questionnaire_code', models.CharField(default='', max_length=64)),
                ('access', models.DateTimeField(auto_now_add=True)),
                ('questionnaire_version', models.IntegerField()),
                ('is_edit_complete', models.BooleanField(default=False)),
                ('user', models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
        ),
        migrations.AlterField(
            model_name='questionnairetranslation',
            name='language',
            field=models.CharField(choices=[('en', 'English'), ('fr', 'French'), ('es', 'Spanish'), ('ru', 'Russian'), ('zh', 'Chinese'), ('km', 'Khmer'), ('lo', 'Lao'), ('ar', 'Arabic'), ('pt', 'Portuguese'), ('af', 'Afrikaans'), ('th', 'Thai'), ('mn', 'Mongolian')], max_length=63),
        ),
    ]

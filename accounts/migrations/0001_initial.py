# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('auth', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='User',
            fields=[
                ('id', models.AutoField(verbose_name='ID', auto_created=True, primary_key=True, serialize=False)),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(verbose_name='last login', default=django.utils.timezone.now)),
                ('is_superuser', models.BooleanField(verbose_name='superuser status', default=False, help_text='Designates that this user has all permissions without explicitly assigning them.')),
                ('email', models.EmailField(verbose_name='email address', unique=True, max_length=255)),
                ('name', models.CharField(blank=True, null=True, max_length=100)),
                ('date_joined', models.DateTimeField(auto_now_add=True)),
                ('groups', models.ManyToManyField(related_name='user_set', related_query_name='user', to='auth.Group', blank=True, verbose_name='groups', help_text='The groups this user belongs to. A user will get all permissions granted to each of his/her group.')),
                ('user_permissions', models.ManyToManyField(related_name='user_set', related_query_name='user', to='auth.Permission', blank=True, verbose_name='user permissions', help_text='Specific permissions for this user.')),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]

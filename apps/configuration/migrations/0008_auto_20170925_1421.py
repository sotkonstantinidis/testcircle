# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import easy_thumbnails.fields


class Migration(migrations.Migration):

    dependencies = [
        ('configuration', '0007_auto_20170925_1307'),
    ]

    operations = [
        migrations.AddField(
            model_name='project',
            name='logo',
            field=easy_thumbnails.fields.ThumbnailerField(blank=True, null=True, upload_to=''),
        ),
        migrations.AddField(
            model_name='project',
            name='url',
            field=models.URLField(blank=True),
        ),
    ]

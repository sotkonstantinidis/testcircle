# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models
import easy_thumbnails.fields


class Migration(migrations.Migration):

    dependencies = [
        ('configuration', '0006_auto_20170810_1651'),
    ]

    operations = [
        migrations.AddField(
            model_name='institution',
            name='external_url',
            field=models.URLField(blank=True),
        ),
        migrations.AddField(
            model_name='institution',
            name='logo',
            field=easy_thumbnails.fields.ThumbnailerField(blank=True, null=True, upload_to=''),
        ),
        migrations.AddField(
            model_name='institution',
            name='url',
            field=models.TextField(blank=True),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djangocms_page_meta', '0008_auto_20160609_0754'),
    ]

    operations = [
        migrations.AddField(
            model_name='pagemeta',
            name='description',
            field=models.CharField(default='', max_length=400, blank=True),
        ),
        migrations.AddField(
            model_name='pagemeta',
            name='gplus_description',
            field=models.CharField(default='', max_length=400, verbose_name='Google+ Description', blank=True),
        ),
        migrations.AddField(
            model_name='pagemeta',
            name='keywords',
            field=models.CharField(default='', max_length=400, blank=True),
        ),
        migrations.AddField(
            model_name='pagemeta',
            name='og_description',
            field=models.CharField(default='', max_length=400, verbose_name='Facebook Description', blank=True),
        ),
        migrations.AddField(
            model_name='pagemeta',
            name='twitter_description',
            field=models.CharField(default='', max_length=140, verbose_name='Twitter Description', blank=True),
        ),
    ]

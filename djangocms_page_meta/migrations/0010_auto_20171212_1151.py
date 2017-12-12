# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('djangocms_page_meta', '0009_auto_20171212_0944'),
    ]

    operations = [
        migrations.AddField(
            model_name='pagemeta',
            name='title',
            field=models.CharField(default='', max_length=400, blank=True),
        ),
        migrations.AlterField(
            model_name='pagemeta',
            name='twitter_type',
            field=models.CharField(blank=True, max_length=255, verbose_name='Twitter Resource type', choices=[('summary', 'Summary Card'), ('summary_large_image', 'Summary Card with Large Image'), ('product', 'Product'), ('photo', 'Photo'), ('player', 'Player'), ('app', 'App')]),
        ),
    ]

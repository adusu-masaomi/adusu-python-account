# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2018-02-28 07:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0016_auto_20180228_1125'),
    ]

    operations = [
        migrations.AddField(
            model_name='partner',
            name='order',
            field=models.IntegerField(blank=True, default=0, verbose_name='ソート順'),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2018-03-12 02:18
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0035_auto_20180312_1116'),
    ]

    operations = [
        migrations.AlterField(
            model_name='partner',
            name='account_number',
            field=models.CharField(blank=True, default='', max_length=16, null=True, verbose_name='口座番号'),
        ),
    ]

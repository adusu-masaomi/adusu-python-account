# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2018-03-12 02:42
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0037_auto_20180312_1120'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='payment_method_id',
            field=models.IntegerField(blank=True, choices=[('', '-'), (1, '振込'), (2, '口座振替'), (3, '現金')], default=0, null=True, verbose_name='支払方法'),
        ),
    ]
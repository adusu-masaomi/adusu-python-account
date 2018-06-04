# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2018-03-22 23:19
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0038_auto_20180312_1142'),
    ]

    operations = [
        migrations.AlterField(
            model_name='partner',
            name='payment_method_id',
            field=models.IntegerField(blank=True, choices=[('', '-'), (1, '振込'), (2, '口座振替'), (3, 'ＡＴＭ'), (4, '現金')], null=True, verbose_name='支払方法ID'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='payment_method_id',
            field=models.IntegerField(blank=True, choices=[('', '-'), (1, '振込'), (2, '口座振替'), (3, 'ＡＴＭ'), (4, '現金')], default=0, null=True, verbose_name='支払方法'),
        ),
    ]

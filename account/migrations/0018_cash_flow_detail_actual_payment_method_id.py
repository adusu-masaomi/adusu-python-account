# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2020-02-01 01:03
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0017_cash_flow_detail_actual_purchase_id'),
    ]

    operations = [
        migrations.AddField(
            model_name='cash_flow_detail_actual',
            name='payment_method_id',
            field=models.IntegerField(choices=[('', '-'), (1, '振込'), (2, '口座振替'), (3, 'ＡＴＭ'), (4, '現金')], default=None, null=True, verbose_name='支払方法ID'),
        ),
    ]

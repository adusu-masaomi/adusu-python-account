# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2020-01-24 00:59
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0004_auto_20200124_0954'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cash_flow_detail_expected',
            name='payment_bank_branch_id',
            field=models.IntegerField(default=None, null=True, verbose_name='支払銀行支店Id'),
        ),
    ]
# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2020-02-01 00:39
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0016_auto_20200131_1055'),
    ]

    operations = [
        migrations.AddField(
            model_name='cash_flow_detail_actual',
            name='purchase_id',
            field=models.IntegerField(default=None, null=True, verbose_name='注文Id'),
        ),
    ]

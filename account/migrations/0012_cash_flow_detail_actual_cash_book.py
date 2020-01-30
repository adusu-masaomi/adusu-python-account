# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2020-01-27 04:37
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0011_auto_20200125_1530'),
    ]

    operations = [
        migrations.AddField(
            model_name='cash_flow_detail_actual',
            name='cash_book',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.SET_NULL, to='account.Cash_Book', verbose_name='出納帳'),
        ),
    ]
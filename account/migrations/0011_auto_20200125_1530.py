# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2020-01-25 06:30
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0010_balance_sheet_tally'),
    ]

    operations = [
        migrations.AlterField(
            model_name='balance_sheet_tally',
            name='borrow_amount',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='貸金額'),
        ),
        migrations.AlterField(
            model_name='balance_sheet_tally',
            name='lend_amount',
            field=models.IntegerField(blank=True, default=0, null=True, verbose_name='借金額'),
        ),
    ]
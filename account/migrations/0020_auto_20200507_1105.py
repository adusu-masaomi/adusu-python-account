# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2020-05-07 02:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0019_auto_20200201_1825'),
    ]

    operations = [
        migrations.AddField(
            model_name='payment',
            name='unpayment_amount',
            field=models.IntegerField(blank=True, null=True, verbose_name='未払金額'),
        ),
        migrations.AddField(
            model_name='payment',
            name='unpayment_date',
            field=models.DateField(blank=True, null=True, verbose_name='未払支払日'),
        ),
    ]

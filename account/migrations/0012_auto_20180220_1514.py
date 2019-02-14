# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2018-02-20 06:14
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0011_auto_20180220_1027'),
    ]

    operations = [
        migrations.AlterField(
            model_name='payment',
            name='payment_date',
            field=models.DateField(blank=True, null=True, verbose_name='支払日'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='payment_due_date',
            field=models.DateField(blank=True, null=True, verbose_name='支払予定日'),
        ),
    ]
# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2018-04-30 23:50
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0043_auto_20180428_1521'),
    ]

    operations = [
        migrations.CreateModel(
            name='PurchaseOrderData',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('purchase_order_code', models.CharField(max_length=255)),
            ],
            options={
                'db_table': 'purchase_order_data',
                'managed': False,
            },
        ),
        migrations.AlterField(
            model_name='cash_book',
            name='staff',
            field=models.ForeignKey(db_constraint=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to='account.Staff', verbose_name='担当者'),
        ),
        migrations.AlterModelTable(
            name='staff',
            table='staffs',
        ),
        migrations.AddField(
            model_name='cash_book',
            name='purchase_order_code',
            field=models.ForeignKey(db_constraint=False, null=True, on_delete=django.db.models.deletion.SET_NULL, to='account.PurchaseOrderData', verbose_name='注文Ｎｏ'),
        ),
    ]

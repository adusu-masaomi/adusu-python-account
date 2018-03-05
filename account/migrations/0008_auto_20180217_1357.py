# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2018-02-17 04:57
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion
#import select2.fields


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0007_auto_20180217_1020'),
    ]

    operations = [
        migrations.CreateModel(
            name='Account_Title',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=255, verbose_name='勘定科目名')),
                ('trade_division_id', models.IntegerField(blank=True, choices=[(0, '経費'), (1, '外注・工事仕入')], default=0, verbose_name='取引区分(0:経費 1:外注等)')),
            ],
        ),
        migrations.DeleteModel(
            name='AccountTitle',
        ),
        migrations.RemoveField(
            model_name='bank_branch',
            name='bank_id',
        ),
        #migrations.AddField(
        #    model_name='bank_branch',
        #    name='bank',
        #    field=select2.fields.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='account.Bank'),
        #),
    ]

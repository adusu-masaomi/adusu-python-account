# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2023-01-27 08:12
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0021_auto_20200507_1422'),
    ]

    operations = [
        migrations.CreateModel(
            name='DailyCashFlow',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('cash_flow_date', models.DateField(verbose_name='入出金日')),
                ('income', models.IntegerField(blank=True, null=True, verbose_name='入金')),
                ('expence', models.IntegerField(blank=True, null=True, verbose_name='出金')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='登録日時')),
                ('update_at', models.DateTimeField(auto_now=True, null=True, verbose_name='更新日時')),
            ],
            options={
                'db_table': 'daily_cash_flows',
                'managed': False,
            },
        ),
        migrations.AddField(
            model_name='payment',
            name='completed_flag',
            field=models.IntegerField(blank=True, null=True, verbose_name='完了フラグ'),
        ),
        migrations.AlterField(
            model_name='partner',
            name='pay_day_division',
            field=models.IntegerField(choices=[(0, '当月'), (1, '翌月'), (2, '翌々月'), (3, '月末(休日前倒し)'), (4, '月末(休日未考慮)'), (5, '翌月末(休日前倒し)'), (6, '翌月末(休日先送り)')], default=0, verbose_name='支払フラグ(月末等)'),
        ),
    ]

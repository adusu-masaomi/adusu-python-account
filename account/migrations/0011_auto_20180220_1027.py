# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2018-02-20 01:27
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0010_auto_20180220_1001'),
    ]

    operations = [
        migrations.CreateModel(
            name='Payment',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('billing_year_month', models.DateField(verbose_name='請求〆年月')),
                ('trade_division_id', models.IntegerField(blank=True, choices=[(0, '経費'), (1, '外注・工事仕入')], default=0, verbose_name='取引区分ID')),
                ('billing_amount', models.IntegerField(blank=True, default=0, verbose_name='支払金額')),
                ('payment_method_id', models.IntegerField(blank=True, choices=[(0, '口座振替'), (1, '振込'), (2, '現金')], default=0, verbose_name='支払方法')),
                ('payment_due_date', models.DateField(verbose_name='支払予定日')),
                ('payment_date', models.DateField(verbose_name='支払日')),
                ('fixed_cost', models.BooleanField(verbose_name='固定費')),
                ('note', models.CharField(max_length=255, verbose_name='備考')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='登録日時')),
                ('update_at', models.DateTimeField(auto_now=True, null=True, verbose_name='更新日時')),
                ('account_title', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='account.Account_Title', verbose_name='科目')),
                ('partner', models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='account.Partner', verbose_name='取引先')),
            ],
        ),
    ]

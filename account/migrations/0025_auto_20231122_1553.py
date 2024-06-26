# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2023-11-22 06:53
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0024_auto_20230405_0953'),
    ]

    operations = [
        migrations.CreateModel(
            name='Daily_Representative_Loan',
            fields=[
                ('id', models.AutoField(primary_key=True, serialize=False)),
                ('table_type_id', models.IntegerField(blank=True, null=True, verbose_name='テーブル種類ID')),
                ('table_id', models.IntegerField(blank=True, null=True, verbose_name='テーブルID')),
                ('occurred_on', models.DateField(verbose_name='発生日')),
                ('account_id', models.IntegerField(blank=True, null=True, verbose_name='科目ID')),
                ('sub_account_id', models.IntegerField(blank=True, null=True, verbose_name='補助科目ID')),
                ('description', models.CharField(max_length=255, verbose_name='摘要')),
                ('debit', models.IntegerField(blank=True, null=True, verbose_name='借方金額')),
                ('credit', models.IntegerField(blank=True, null=True, verbose_name='貸方金額')),
                ('created_at', models.DateTimeField(auto_now_add=True, null=True, verbose_name='登録日時')),
                ('updated_at', models.DateTimeField(auto_now=True, null=True, verbose_name='更新日時')),
            ],
        ),
        
    ]

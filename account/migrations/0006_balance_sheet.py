# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2020-01-24 08:05
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0005_auto_20200124_0959'),
    ]

    operations = [
        migrations.CreateModel(
            name='Balance_Sheet',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('accrual_date', models.DateField(blank=True, null=True, verbose_name='発生日')),
                ('borrow_lend_id', models.IntegerField(default=0, verbose_name='貸借Id')),
                ('amount', models.IntegerField(blank=True, default=0, verbose_name='貸借金額')),
                ('bank_id', models.IntegerField(blank=True, default=None, null=True, verbose_name='銀行Id')),
                ('account_id', models.IntegerField(blank=True, default=None, null=True, verbose_name='科目Id')),
                ('description', models.CharField(max_length=255, verbose_name='適用')),
            ],
        ),
    ]

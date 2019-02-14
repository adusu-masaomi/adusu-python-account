# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2018-02-28 02:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0014_auto_20180220_1530'),
    ]

    operations = [
        migrations.AddField(
            model_name='partner',
            name='fixed_content_id',
            field=models.IntegerField(choices=[(0, ''), (1, '項目のみ'), (2, '項目のみ（指定月）'), (3, '項目・固定費'), (4, '項目・固定費（指定月）'), (5, '項目・概算＝仕入金額')], default=0, verbose_name='固定項目フラグ'),
        ),
        migrations.AddField(
            model_name='partner',
            name='fixed_cost',
            field=models.IntegerField(blank=True, default=0, verbose_name='固定費'),
        ),
        migrations.AddField(
            model_name='partner',
            name='rough_estimate',
            field=models.IntegerField(blank=True, default=0, verbose_name='概算'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='account_title',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='account.Account_Title', verbose_name='項目'),
        ),
        migrations.AlterField(
            model_name='payment',
            name='note',
            field=models.CharField(blank=True, max_length=255, verbose_name='備考'),
        ),
    ]
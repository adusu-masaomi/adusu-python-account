# -*- coding: utf-8 -*-
# Generated by Django 1.9.2 on 2024-03-15 03:16
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('account', '0029_sub_account'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Sub_Account',
            new_name='Account_Sub',
        ),
    ]

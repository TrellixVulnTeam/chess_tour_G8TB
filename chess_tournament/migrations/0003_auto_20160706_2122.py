# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-06 18:22
from __future__ import unicode_literals

from django.db import migrations


class Migration(migrations.Migration):

    dependencies = [
        ('chess_tournament', '0002_auto_20160706_1957'),
    ]

    operations = [
        migrations.AlterModelOptions(
            name='chess',
            options={'verbose_name': 'Chess', 'verbose_name_plural': 'Chess'},
        ),
    ]
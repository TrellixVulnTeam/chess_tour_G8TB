# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-07 15:38
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chess_tournament', '0004_auto_20160707_1440'),
    ]

    operations = [
        migrations.AddField(
            model_name='tounament',
            name='is_finished',
            field=models.BooleanField(default=False),
        ),
        migrations.AlterField(
            model_name='tounament',
            name='name',
            field=models.CharField(max_length=100),
        ),
    ]

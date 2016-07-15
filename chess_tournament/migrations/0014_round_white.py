# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-10 17:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chess_tournament', '0013_auto_20160710_1905'),
    ]

    operations = [
        migrations.AddField(
            model_name='round',
            name='white',
            field=models.CharField(choices=[('1', 'player_1'), ('2', 'player_2')], default=1, max_length=1),
            preserve_default=False,
        ),
    ]

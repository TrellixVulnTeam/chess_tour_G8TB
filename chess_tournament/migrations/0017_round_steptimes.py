# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-10 21:53
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chess_tournament', '0016_round_winnerid'),
    ]

    operations = [
        migrations.AddField(
            model_name='round',
            name='stepTimes',
            field=models.TextField(blank=True, default=''),
        ),
    ]
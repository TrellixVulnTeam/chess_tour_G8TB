# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-07 17:03
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('chess_tournament', '0008_auto_20160707_2002'),
    ]

    operations = [
        migrations.AlterField(
            model_name='round',
            name='tour',
            field=models.OneToOneField(null=True, on_delete=django.db.models.deletion.CASCADE, to='chess_tournament.Tournament'),
        ),
    ]

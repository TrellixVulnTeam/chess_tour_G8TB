# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-07 15:49
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('chess_tournament', '0006_auto_20160707_1843'),
    ]

    operations = [
        migrations.RenameModel(
            old_name='Tounament',
            new_name='Tournament',
        ),
        migrations.AlterModelOptions(
            name='tournament',
            options={'verbose_name': 'Tournament', 'verbose_name_plural': 'Tournaments'},
        ),
        migrations.AlterField(
            model_name='round',
            name='EndTime',
            field=models.TimeField(),
        ),
        migrations.AlterField(
            model_name='round',
            name='StartTime',
            field=models.TimeField(),
        ),
    ]

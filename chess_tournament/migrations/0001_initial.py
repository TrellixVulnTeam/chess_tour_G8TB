# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-06 16:22
from __future__ import unicode_literals

import builtins
import chess_tournament.models
import datetime
from django.conf import settings
import django.contrib.auth.models
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    initial = True

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('auth', '0007_alter_validators_add_error_messages'),
    ]

    operations = [
        migrations.CreateModel(
            name='CustomUser',
            fields=[
                ('user_ptr', models.OneToOneField(auto_created=True, on_delete=django.db.models.deletion.CASCADE, parent_link=True, primary_key=True, serialize=False, to=settings.AUTH_USER_MODEL)),
                ('last_activity', models.DateTimeField(default=datetime.datetime(1970, 1, 1, 0, 0))),
                ('is_avaliable', models.BooleanField(default=False)),
                ('in_progress', models.BooleanField(default=False)),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
                'abstract': False,
            },
            bases=('auth.user',),
            managers=[
                ('objects', django.contrib.auth.models.UserManager()),
            ],
        ),
        migrations.CreateModel(
            name='Round',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default='<built-in function id>', max_length=100)),
                ('StartTime', models.TimeField()),
                ('EndTime', models.TimeField()),
                ('History', models.TextField()),
                ('player_1', models.OneToOneField(on_delete=models.SET(chess_tournament.models.get_sentinel_user), related_name='pleyer_one', to=settings.AUTH_USER_MODEL)),
                ('player_2', models.OneToOneField(on_delete=models.SET(chess_tournament.models.get_sentinel_user), related_name='pleyer_two', to=settings.AUTH_USER_MODEL)),
            ],
            options={
                'verbose_name': 'Round',
                'verbose_name_plural': 'Rounds',
            },
        ),
        migrations.CreateModel(
            name='Tounament',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(default=builtins.id, max_length=100)),
                ('date', models.DateField(auto_now_add=True)),
                ('time', models.TimeField()),
                ('roundTmeLimit', models.IntegerField(default=0)),
                ('playersCount', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name': 'Tounament',
                'verbose_name_plural': 'Tounaments',
            },
        ),
        migrations.CreateModel(
            name='Tour_Round',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('round_id', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='chess_tournament.Round')),
                ('tour_id', models.OneToOneField(on_delete=django.db.models.deletion.CASCADE, to='chess_tournament.Tounament')),
            ],
            options={
                'verbose_name': 'Tour_Round',
                'verbose_name_plural': 'Tour_Rounds',
            },
        ),
    ]

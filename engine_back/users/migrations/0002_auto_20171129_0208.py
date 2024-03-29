# -*- coding: utf-8 -*-
# Generated by Django 1.11.5 on 2017-11-28 17:08
from __future__ import unicode_literals

from django.conf import settings
from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('users', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Query',
            fields=[
                ('id', models.AutoField(auto_created=True, primary_key=True, serialize=False, verbose_name='ID')),
                ('words', models.CharField(max_length=100)),
            ],
        ),
        migrations.RemoveField(
            model_name='user',
            name='author',
        ),
        migrations.RemoveField(
            model_name='user',
            name='profile_photo',
        ),
        migrations.AddField(
            model_name='query',
            name='author',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='log', to=settings.AUTH_USER_MODEL),
        ),
    ]

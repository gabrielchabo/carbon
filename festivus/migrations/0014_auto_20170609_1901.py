# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-09 16:01
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('festivus', '0013_auto_20170605_1928'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='event',
            name='budget',
        ),
        migrations.RemoveField(
            model_name='event',
            name='currency',
        ),
        migrations.AddField(
            model_name='transaction',
            name='membership',
            field=models.ForeignKey(blank=True, null=True, on_delete=django.db.models.deletion.CASCADE, to='festivus.Membership'),
        ),
    ]

# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-05 16:06
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('festivus', '0009_auto_20170604_1930'),
    ]

    operations = [
        migrations.AddField(
            model_name='transaction',
            name='description',
            field=models.CharField(blank=True, max_length=10),
        ),
    ]
# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-06-04 05:58
from __future__ import unicode_literals

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('festivus', '0001_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='person',
            name='team',
            field=models.ForeignKey(null=True, on_delete=django.db.models.deletion.CASCADE, to='festivus.Team'),
        ),
    ]

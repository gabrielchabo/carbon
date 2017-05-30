# -*- coding: utf-8 -*-
# Generated by Django 1.11.1 on 2017-05-30 16:02
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('festivus', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='person',
            name='marital_status',
            field=models.CharField(choices=[('S', 'Single'), ('E', 'Engaged'), ('D', 'Married'), ('W', 'Windowed'), ('C', 'Complicated')], default='S', max_length=10),
        ),
    ]

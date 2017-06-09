# -*- coding: utf-8 -*-
# Generated by Django 1.11.2 on 2017-06-05 16:28
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('festivus', '0012_auto_20170605_1927'),
    ]

    operations = [
        migrations.AlterField(
            model_name='membership',
            name='amount',
            field=models.DecimalField(decimal_places=2, default=10, max_digits=15),
        ),
        migrations.AlterField(
            model_name='payment',
            name='amount',
            field=models.DecimalField(decimal_places=2, default=10, max_digits=15),
        ),
        migrations.AlterField(
            model_name='transaction',
            name='amount',
            field=models.DecimalField(decimal_places=2, default=10, max_digits=15),
        ),
    ]

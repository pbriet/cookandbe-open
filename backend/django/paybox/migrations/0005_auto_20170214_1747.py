# -*- coding: utf-8 -*-
# Generated by Django 1.9.12 on 2017-02-14 16:47
from __future__ import unicode_literals

import django.core.validators
from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('paybox', '0004_globalspecialoffer'),
    ]

    operations = [
        migrations.AlterField(
            model_name='subscription',
            name='level',
            field=models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(1)]),
        ),
    ]

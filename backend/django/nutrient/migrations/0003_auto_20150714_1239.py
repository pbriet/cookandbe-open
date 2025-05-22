# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nutrient', '0002_auto_20150609_1214'),
    ]

    operations = [
        migrations.AlterField(
            model_name='nutrient',
            name='key',
            field=models.CharField(unique=True, max_length=50),
            preserve_default=True,
        ),
    ]

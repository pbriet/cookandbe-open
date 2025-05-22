# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipe_mgr', '0009_diet_specific_tags'),
    ]

    operations = [
        migrations.AlterField(
            model_name='foodconversion',
            name='food',
            field=models.ForeignKey(on_delete=models.CASCADE, to='recipe_mgr.Food', related_name='conversions'),
        ),
        migrations.AlterField(
            model_name='recipeinstruction',
            name='text',
            field=models.TextField(blank=True),
        ),
    ]

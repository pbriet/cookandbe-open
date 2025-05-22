# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def mergeEnableAndInternal(apps, schema_editor):
    Food        = apps.get_model("recipe_mgr", "Food")
    for food in Food.objects.filter(internal = True):
        food.enabled = False
        food.save()

class Migration(migrations.Migration):

    dependencies = [
        ('recipe_mgr', '0004_ingredient_simplification'),
    ]

    operations = [
        migrations.RunPython(mergeEnableAndInternal),
        migrations.RemoveField(
            model_name='food',
            name='internal',
        ),
    ]

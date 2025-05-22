# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def createGluttenFreeDiet(apps, schema_editor):
    Diet    = apps.get_model("diet_mgr", "Diet")
    FoodTag = apps.get_model("recipe_mgr", "FoodTag")
    
    gluttenFreeDiet = Diet.objects.create(
        key = "gluten_free", title = "Sans gluten", min_subscription_level = 2, has_diagnostic = False, enabled = False,
        description = "Une alimentation sans blé, seigle, orge, ni avoine.", url_key = "sans-gluten", free_trial_days = 14,
        email_title = "L'alimentation sans gluten"
    )
    # Exclusions
    glutenTag = FoodTag.objects.get(name = "Gluten")
    gluttenFreeDiet.excluded_food_tags.add(glutenTag)
    gluttenFreeDiet.save()

def deleteGluttenFreeDiet(apps, schema_editor):
    Diet = apps.get_model("diet_mgr", "Diet")
    Diet.objects.filter(key = "gluten_free").delete()

class Migration(migrations.Migration):

    dependencies = [
        ('diet_mgr', '0002_auto_20150609_1214'),
    ]

    operations = [
        # migrations.RunPython(createGluttenFreeDiet, deleteGluttenFreeDiet)
    ]

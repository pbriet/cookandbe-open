# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def createVeganDiet(apps, schema_editor):
    Diet    = apps.get_model("diet_mgr", "Diet")
    FoodTag = apps.get_model("recipe_mgr", "FoodTag")
    
    veganDiet = Diet.objects.create(
        key = "vegetarian", title = "Végétarien", min_subscription_level = 2, has_diagnostic = False, enabled = False,
        description = "Une alimentation interdisant la consommation de chaire animale.", url_key = "vegetarien", free_trial_days = 14,
        email_title = "L'alimentation végétarienne"
    )
    # Exclusions
    for tag_name in ("Viande", "Poisson", "Fruits de mer"):
        food_tag = FoodTag.objects.get(name = tag_name)
        veganDiet.excluded_food_tags.add(food_tag)
    veganDiet.save()

def deleteVeganDiet(apps, schema_editor):
    Diet = apps.get_model("diet_mgr", "Diet")
    Diet.objects.filter(key = "vegetarian").delete()

class Migration(migrations.Migration):

    dependencies = [
        ('diet_mgr', '0003_adding_glutten_free'),
        ('recipe_mgr', '0009_diet_specific_tags'),
    ]

    operations = [
        # migrations.RunPython(createVeganDiet, deleteVeganDiet)
    ]

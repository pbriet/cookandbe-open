# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def createVeganFundamentalismDiet(apps, schema_editor):
    Diet    = apps.get_model("diet_mgr", "Diet")
    FoodTag = apps.get_model("recipe_mgr", "FoodTag")
    
    # Exclusions vegetaliennes
    veganDiet = Diet.objects.create(
        key = "vegan",
        title = "Végan / Végétalien",
        min_subscription_level = 0,
        has_diagnostic = False,
        enabled = False,
        description = "Entrez dans l'univers vegan sans chair ni produits d'origine animale.",
        url_key = "vegan",
        free_trial_days = 14,
        email_title = "L'alimentation végétalienne",
    )
    animalOriginTag = FoodTag.objects.get(name = "Origine animale")
    animalFleshTag  = FoodTag.objects.get(name = "Chair animale")
    veganDiet.excluded_food_tags.add(animalOriginTag)
    veganDiet.excluded_food_tags.add(animalFleshTag)
    veganDiet.save()
    # Mises à jour
    vegetarianDiet = Diet.objects.get(key="vegetarian")
    for food_tag in vegetarianDiet.excluded_food_tags.all():
        vegetarianDiet.excluded_food_tags.remove(food_tag)
    vegetarianDiet.excluded_food_tags.add(animalFleshTag)
    vegetarianDiet.description = "Des idées repas équilibrées sans viande, sans poisson, sans fruits de mer, mais surtout sans carences !"
    vegetarianDiet.save()
    glutenDiet = Diet.objects.get(key="gluten_free")
    glutenDiet.description = "Mangez sans blé, seigle, orge ni avoine tout en conservant un équilibre alimentaire optimal !"
    glutenDiet.save()

class Migration(migrations.Migration):

    dependencies = [
        ('diet_mgr', '0007_diet_level_update_2'),
        ('recipe_mgr', '0013_vegan_specific_tags'),
    ]

    operations = [
        # migrations.RunPython(createVeganFundamentalismDiet, None)
    ]

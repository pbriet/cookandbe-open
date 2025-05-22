# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipe_mgr', '0007_auto_20150811_1500'),
    ]

    
    def remove_garlic_grams(apps, schema_editor):
         Ingredient = apps.get_model("recipe_mgr", "Ingredient")
         Food = apps.get_model("recipe_mgr", "Food")
         FoodConversion = apps.get_model("recipe_mgr", "FoodConversion")
         
         food = Food.objects.get(name="Ail")
         
         grams  = FoodConversion.objects.get(food=food, unit="g")
         gousse = FoodConversion.objects.get(food=food, unit="gousse")
         
         ingredients = Ingredient.objects.filter(default_conversion_id = grams.id)
         
         for ingredient in ingredients:
             print(ingredient.recipe.name, ingredient.food.name)
             ingredient.default_conversion_id = gousse.id
             ingredient.save()
         
         grams.delete()
             

    operations = [
        # migrations.RunPython(remove_garlic_grams)
    ]
    
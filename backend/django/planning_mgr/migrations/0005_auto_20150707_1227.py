# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    def dish_options_check(apps, schema_editor):
        
        MealDishOption = apps.get_model("planning_mgr", "MealDishOption")
        
        # Mealtype/Dishtype -> Time min / Budget min
        VALUES = {
            
            "Petit déjeuner Petit déjeuner (base)": (1, 1),
            "Petit déjeuner Boisson chaude" : (1, 1),
            "Petit déjeuner Boisson froide" : (None, None),
            "Petit déjeuner Fruit" : (None, None),
            
            "Collation Snack salé" : (None, None),
            "Collation Fruit" : (1, 1),
            "Collation Boisson froide" : (None, None),
            "Collation Boisson chaude" : (None, None),
            "Collation Snack sucré" : (None, None),
            
            "Déjeuner Entrée" : (3, 2),
            "Déjeuner Plat complet" : (1, 1),
            "Déjeuner Dessert" : (1, 1),
            "Déjeuner Pain" : (1, 1),
            "Déjeuner Fromage" : (2, 2),
            "Déjeuner Boisson froide" : (None, None),
            "Déjeuner Boisson chaude" : (None, None),
            
            "Goûter Snack sucré" : (1, 1),
            "Goûter Snack salé" : (None, None),
            "Goûter Fruit" : (3, 1),
            "Goûter Boisson froide" : (None, None),
            "Goûter Boisson chaude" : (None, None),
            
            "Dîner Entrée" : (2, 2),
            "Dîner Plat complet" : (1, 1),
            "Dîner Pain" : (1, 1),
            "Dîner Dessert" : (1, 1),
            "Dîner Fromage" : (1, 1),
            "Dîner Boisson froide" : (None, None),
            "Dîner Boisson chaude" : (None, None)
        }
        
        nb = 0
        for do in MealDishOption.objects.all():
            key = "%s %s" % (do.meal_type.name, do.dish_type.name)
            assert key in VALUES, "undefined key : %s" % key
            nb += 1
            do.min_speed_check, do.min_budget_check = VALUES[key]
            do.save()
        
        assert len(VALUES) == nb, "Missing dish option ?"

    dependencies = [
        ('planning_mgr', '0004_auto_20150707_1227'),
    ]

    operations = [
        # migrations.RunPython(dish_options_check),
    ]

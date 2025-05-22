# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def addGlutenWarning(apps, schema_editor):
    Diet    = apps.get_model("diet_mgr", "Diet")
    FoodTag = apps.get_model("recipe_mgr", "FoodTag")
    
    glutenDiet      = Diet.objects.get(key="gluten_free")
    glutenWarning   = FoodTag.objects.get(name="Traces de gluten")
    glutenDiet.forewarned_food_tags.add(glutenWarning)
    glutenDiet.save()

class Migration(migrations.Migration):

    dependencies = [
        ('recipe_mgr', '0010_auto_20150903_1819'),
        ('diet_mgr', '0004_adding_vegan'),
    ]

    operations = [
        migrations.AddField(
            model_name='diet',
            name='forewarned_food_tags',
            field=models.ManyToManyField(related_name='diets_with_warning', to='recipe_mgr.FoodTag'),
        ),
        # migrations.RunPython(addGlutenWarning),
    ]

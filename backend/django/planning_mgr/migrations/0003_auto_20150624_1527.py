# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    def fix_empty_meals(apps, schema_editor):
         MetaPlanning = apps.get_model("planning_mgr", "MetaPlanning")
         Dish         = apps.get_model("planning_mgr", "Dish")
         DishType     = apps.get_model("recipe_mgr", "DishType")
         
         dt_fruit = DishType.objects.get(name="Fruit")
         
         for planning in MetaPlanning.objects.filter(planning=None).prefetch_related('days__meal_slots__dishes__dish_type'):
             if planning.id != planning.user.meta_planning_id:
                 print("deleting obsolete metaplanning (%s)" % planning.user.email)
                 planning.delete()
             for day in planning.days.all():
                for meal_slot in day.meal_slots.all():
                    dish_types = []
                    for dish in meal_slot.dishes.all():
                        dish_types.append(dish.dish_type.name)
                    
                    if dish_types == ["Personnalisé"] and\
                        meal_slot.meal_type.name in ("Goûter", "Collation", "Petit déjeuner"):
                        
                        Dish.objects.create(dish_type=dt_fruit, meal_slot=meal_slot, order=0)
                        print("fixing missing dish : %s" % planning.user.email)
          
    dependencies = [
        ('planning_mgr', '0002_auto_20150609_1214'),
    ]

    operations = [
        # migrations.RunPython(fix_empty_meals),
    ]

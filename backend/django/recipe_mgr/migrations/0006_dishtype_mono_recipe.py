# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipe_mgr', '0005_remove_food_internal'),
    ]
    
    def set_monotonous_dishtypes(apps, schema_editor):
         DishType = apps.get_model("recipe_mgr", "DishType")
         
         
         mono_dishtypes = ["Pain", "Boisson chaude", "Petit déjeuner (base)"]
         
         for dish_type in DishType.objects.filter(name__in=mono_dishtypes):
             dish_type.monotonous = True
             dish_type.save()
             

    operations = [
        migrations.AddField(
            model_name='dishtype',
            name='monotonous',
            field=models.BooleanField(default=False),
            preserve_default=True,
        ),
        migrations.RunPython(set_monotonous_dishtypes)
    ]

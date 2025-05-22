# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def update_diet_levels(apps, schema_editor):
    Diet    = apps.get_model("diet_mgr", "Diet")
    
    for diet_key in ("gluten_free", "vegetarian"):
        diet = Diet.objects.get(key=diet_key)
        diet.min_subscription_level = 1
        diet.free_trial_days = 7
        diet.save()

class Migration(migrations.Migration):

    dependencies = [
        ('diet_mgr', '0005_diet_forewarned_food_tags'),
    ]

    operations = [
        # migrations.RunPython(update_diet_levels),
    ]

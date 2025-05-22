# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipe_mgr', '0008_remove_garlic_grams'),
    ]

    def create_specific_tags(apps, schema_editor):
        FoodTag = apps.get_model("recipe_mgr", "FoodTag")
        
        FoodTag.objects.create(
            id = 11,
            name = "Traces de gluten",
            can_be_disliked = False,
        )
    
    def delete_specific_tags(apps, schema_editor):
        FoodTag = apps.get_model("recipe_mgr", "FoodTag")
        FoodTag.objects.get(pk=11).delete()

    operations = [
        migrations.RunPython(create_specific_tags, delete_specific_tags),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipe_mgr', '0012_cookbook2'),
    ]

    def create_specific_tags(apps, schema_editor):
        FoodTag = apps.get_model("recipe_mgr", "FoodTag")

        animalOriginTag = FoodTag.objects.create(name="Origine animale", can_be_disliked=False, id=12)
        for tag_name in ("Oeuf", "Miel", "Lait", "Fromage"):
            food_tag = FoodTag.objects.get(name = tag_name)
            animalOriginTag.children.add(food_tag)
        animalOriginTag.save()
        animalFleshTag = FoodTag.objects.create(name="Chair animale", can_be_disliked=False, id=13)
        for tag_name in ("Viande", "Poisson", "Fruits de mer"):
            food_tag = FoodTag.objects.get(name = tag_name)
            animalFleshTag.children.add(food_tag)
        animalFleshTag.save()

    def delete_specific_tags(apps, schema_editor):
        FoodTag = apps.get_model("recipe_mgr", "FoodTag")
        FoodTag.objects.get(pk__in=(11, 12)).delete()

    operations = [
        # migrations.RunPython(create_specific_tags, delete_specific_tags),
    ]

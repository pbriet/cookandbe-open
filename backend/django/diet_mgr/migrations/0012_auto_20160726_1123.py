# -*- coding: utf-8 -*-
# Generated by Django 1.9.7 on 2016-07-26 09:23
from __future__ import unicode_literals

from django.db import migrations


def update_diet_descriptions(apps, schema_editor):
    Diet    = apps.get_model("diet_mgr", "Diet")

    new_description = {
        "balanced" : "Testez le rééquilibrage alimentaire avec le menu équilibré par Cook&Be. Retrouvez des idées de menus équilibrés et personnalisés pour la semaine",
        "gluten_free": "Testez nos menus sans gluten pour un rééquilibrage alimentaire. Cook&Be vous propose des menus personnalisés et équilibrés sans pain, sans farine et sans pâtes",
        "vegetarian": "Testez nos menus végétariens pour un rééquilibrage alimentaire. Cook&Be vous propose des menus sans viande, sans poisson ni fruits de mer pour toute la semaine",
    }

    for diet in Diet.objects.all():
        if diet.key in new_description:
            diet.description = new_description[diet.key]
            diet.save()
    
class Migration(migrations.Migration):

    dependencies = [
        ('diet_mgr', '0011_auto_20160629_1207'),
    ]

    operations = [
        # migrations.RunPython(update_diet_descriptions)
    ]

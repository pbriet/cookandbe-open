# -*- coding: utf-8 -*-
# Generated by Django 1.11.7 on 2018-01-05 14:58
from __future__ import unicode_literals

from django.db import migrations



def remove_health_diets(apps, schema_editor):
    Diet    = apps.get_model("diet_mgr", "Diet")

    Diet.objects.filter(key__in=["easy_digest", "hypertension", "normolipidic", "diabete", "cardiovascular"]).update(enabled=False)

class Migration(migrations.Migration):

    dependencies = [
        ('diet_mgr', '0013_auto_20161209_1842'),
    ]

    operations = [
        migrations.RunPython(remove_health_diets)
    ]


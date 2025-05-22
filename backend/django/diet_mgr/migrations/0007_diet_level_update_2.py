# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


def set_them_free(apps, schema_editor):
    """
    Set the "freedom" diets free
    """
    Diet    = apps.get_model("diet_mgr", "Diet")
    
    for diet in Diet.objects.filter(min_subscription_level=1):
        diet.min_subscription_level = 0
        if diet.key == "easy_digest" :
            diet.enabled = False
        if diet.key == "vegetarian" :
            diet.enabled = True
        diet.save()
        
    for diet in Diet.objects.filter(min_subscription_level=2):
        diet.enabled = False
        diet.save()

class Migration(migrations.Migration):

    dependencies = [
        ('diet_mgr', '0006_diet_level_update'),
    ]

    operations = [
        migrations.RunPython(set_them_free),
    ]

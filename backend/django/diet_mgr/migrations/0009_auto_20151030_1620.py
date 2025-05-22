# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


def renameBalancedDiet(apps, schema_editor):
    Diet    = apps.get_model("diet_mgr", "Diet")
    
    balanced = Diet.objects.get(title="Manger équilibré")
    balanced.title = "Classique"
    balanced.save()

class Migration(migrations.Migration):

    dependencies = [
        ('diet_mgr', '0008_adding_vegan_fundamentalism'),
    ]
    
    
    operations = [
        # migrations.RunPython(renameBalancedDiet, None)
    ]

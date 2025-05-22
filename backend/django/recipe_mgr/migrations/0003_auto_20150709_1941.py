# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def freshToStorage(apps, schema_editor):
    fresh_expiries = {
        5: 2,  # Volaille
        7: 2,  # Saucisse & viande froide
        10: 4, # Porc
        13: 4, # Boeuf
        15: 2, # Poisson, crustacés
        17: 4, # Agneau, veau, gibier
        ## CNF ##
        36: 2, # Poisson
        47: 4, # Viande
        48: 2, # Volaille
        49: 2, # Abats
        51: 2, # Poisson
        52: 2, # Crustacés, mollusques
        64: 4, # Sandwich
        69: 2, # Poisson
        77: 2, # Crustacés, mollusques
        99: 2, # Crustacés, mollusques
    }
    FoodType = apps.get_model("recipe_mgr", "FoodType")
    for ft in FoodType.objects.all():
        ft.usually_stored = not ft.usually_stored
        if ft.id in fresh_expiries:
            ft.fresh_expiry = fresh_expiries[ft.id]
        ft.save()

class Migration(migrations.Migration):

    dependencies = [
        ('recipe_mgr', '0002_auto_20150609_1214'),
    ]

    operations = [
        migrations.RenameField(
            model_name='foodtype',
            old_name='is_fresh',
            new_name='usually_stored',
        ),
        migrations.AddField(
            model_name='food',
            name='fresh_expiry',
            field=models.IntegerField(blank=True, null=True, default=None),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='foodtype',
            name='fresh_expiry',
            field=models.IntegerField(blank=True, null=True, default=None),
            preserve_default=True,
        ),
        # migrations.RunPython(freshToStorage, freshToStorage),
    ]

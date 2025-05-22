# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations

def init_category_list_order(apps, schema_editor):
    Category = apps.get_model("shopping_mgr", "ShoppingCategory")
    
    # New categories
    special_categories = ("Autre", "Surgelés", "Conserves")
    for category_name in special_categories:
        Category.objects.create(name = category_name)

    # Fixing order
    category_orders = {
        "Autre": 1,
        "Fruits et légumes": 2,
        "Viande et charcuterie": 3,
        "Poissons et fruits de mer": 4,
        "Rayon frais": 5,
        "Surgelés": 6,
        "Produits laitiers": 7,
        "Pain et viennoiserie": 8,
        "Conserves": 9,
        "Boissons": 10,
        "Soupes et potages": 11,
        "Produits bébés": 12,
        "Gateaux et confiseries": 13,
        "Petit déjeuner et boissons chaudes": 14,
        "Pâtes, riz et féculents": 15,
        "Epicerie sucrée": 16,
        "Condiments et sauces": 17,
        "Epicerie": 18,
        "Rayon diététique": 19,
        "Cuisine": 20,
    }
    for category in Category.objects.all():
        category.list_order = category_orders[category.name]
        category.save()
    

class Migration(migrations.Migration):

    dependencies = [
        ('shopping_mgr', '0004_auto_20150708_1540'),
    ]

    operations = [
        migrations.AddField(
            model_name='shoppingcategory',
            name='list_order',
            field=models.IntegerField(null=True, default=None),
            preserve_default=True,
        ),
        migrations.RunPython(init_category_list_order),
    ]

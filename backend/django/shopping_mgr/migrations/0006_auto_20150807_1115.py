# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shopping_mgr', '0005_shoppingcategory_list_order'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='textshoppingitem',
            name='shopping_category',
        ),
        migrations.RemoveField(
            model_name='textshoppingitem',
            name='shopping_list',
        ),
        migrations.DeleteModel(
            name='TextShoppingItem',
        ),
    ]

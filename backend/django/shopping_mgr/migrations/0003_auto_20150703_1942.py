# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shopping_mgr', '0002_shoppingitem_forced_name'),
    ]

    operations = [
        migrations.AlterField(
            model_name='shoppingitem',
            name='food',
            field=models.ForeignKey(on_delete=models.CASCADE, null=True, to='recipe_mgr.Food'),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='shoppingitem',
            name='grams',
            field=models.FloatField(null=True),
            preserve_default=True,
        ),
        migrations.AlterField(
            model_name='shoppingitem',
            name='raw_state',
            field=models.ForeignKey(on_delete=models.CASCADE, null=True, to='recipe_mgr.RawState'),
            preserve_default=True,
        ),
    ]

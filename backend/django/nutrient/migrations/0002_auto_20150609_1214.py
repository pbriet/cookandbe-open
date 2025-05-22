# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('nutrient', '0001_initial'),
        ('recipe_mgr', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='nutrientrawstatealteration',
            name='raw_state',
            field=models.ForeignKey(on_delete=models.CASCADE, to='recipe_mgr.RawState'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='nutrientcookalteration',
            name='cooking_method',
            field=models.ForeignKey(on_delete=models.CASCADE, to='recipe_mgr.CookingMethod'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='nutrientcookalteration',
            name='nutrient',
            field=models.ForeignKey(on_delete=models.CASCADE, to='nutrient.Nutrient'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='foodnutrient',
            name='cooking_method',
            field=models.ForeignKey(on_delete=models.CASCADE, to='recipe_mgr.CookingMethod'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='foodnutrient',
            name='food',
            field=models.ForeignKey(on_delete=models.CASCADE, editable=False, to='recipe_mgr.Food', related_name='food_nutrients'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='foodnutrient',
            name='nutrient',
            field=models.ForeignKey(on_delete=models.CASCADE, editable=False, to='nutrient.Nutrient'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='foodnutrient',
            name='raw_state',
            field=models.ForeignKey(on_delete=models.CASCADE, to='recipe_mgr.RawState'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='foodnutrient',
            unique_together=set([('food', 'nutrient', 'cooking_method', 'raw_state')]),
        ),
        migrations.AddField(
            model_name='cookingmethodeffect',
            name='cooking_method',
            field=models.ForeignKey(on_delete=models.CASCADE, to='recipe_mgr.CookingMethod'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='cookingmethodeffect',
            name='food_type',
            field=models.ForeignKey(on_delete=models.CASCADE, to='recipe_mgr.FoodType'),
            preserve_default=True,
        ),
    ]

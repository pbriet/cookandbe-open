# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('eater_mgr', '0001_initial'),
        ('shopping_mgr', '0001_initial'),
        ('planning_mgr', '0001_initial'),
        ('recipe_mgr', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='notnow',
            name='recipe',
            field=models.ForeignKey(on_delete=models.CASCADE, to='recipe_mgr.Recipe'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='notnow',
            name='user',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='not_nows', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='metaplanning',
            name='user',
            field=models.ForeignKey(on_delete=models.CASCADE, to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mealtype',
            name='default_place',
            field=models.ForeignKey(on_delete=models.CASCADE, to='planning_mgr.MealPlace'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mealtype',
            name='dish_types',
            field=models.ManyToManyField(through='planning_mgr.MealDishOption', to='recipe_mgr.DishType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mealtype',
            name='static_recipe_options',
            field=models.ManyToManyField(to='recipe_mgr.Recipe'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mealsloteater',
            name='eater',
            field=models.ForeignKey(on_delete=models.CASCADE, to='eater_mgr.Eater'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mealsloteater',
            name='meal_slot',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='meal_slot_eaters', to='planning_mgr.MealSlot'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mealslot',
            name='day',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='meal_slots', to='planning_mgr.Day'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mealslot',
            name='eaters',
            field=models.ManyToManyField(through='planning_mgr.MealSlotEater', to='eater_mgr.Eater'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mealslot',
            name='meal_place',
            field=models.ForeignKey(on_delete=models.CASCADE, to='planning_mgr.MealPlace'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mealslot',
            name='meal_type',
            field=models.ForeignKey(on_delete=models.CASCADE, to='planning_mgr.MealType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mealdishoption',
            name='default_recipe',
            field=models.ForeignKey(on_delete=models.CASCADE, null=True, to='recipe_mgr.Recipe'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mealdishoption',
            name='dish_type',
            field=models.ForeignKey(on_delete=models.CASCADE, to='recipe_mgr.DishType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mealdishoption',
            name='meal_type',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='dish_options', to='planning_mgr.MealType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dishrecipefilter',
            name='dish',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='dish_recipe_filters', to='planning_mgr.Dish'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dishrecipefilter',
            name='dish_type',
            field=models.ForeignKey(on_delete=models.CASCADE, to='recipe_mgr.DishType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dishrecipefilter',
            name='recipe_tag',
            field=models.ForeignKey(on_delete=models.CASCADE, to='recipe_mgr.RecipeTag'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dishrecipe',
            name='dish',
            field=models.ForeignKey(on_delete=models.CASCADE, to='planning_mgr.Dish'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dishrecipe',
            name='recipe',
            field=models.ForeignKey(on_delete=models.CASCADE, to='recipe_mgr.Recipe'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dishrecipe',
            name='user',
            field=models.ForeignKey(on_delete=models.CASCADE, default=None, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dishfoodfilter',
            name='dish',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='dish_food_filters', to='planning_mgr.Dish'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dishfoodfilter',
            name='dish_type',
            field=models.ForeignKey(on_delete=models.CASCADE, to='recipe_mgr.DishType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dishfoodfilter',
            name='food_tag',
            field=models.ForeignKey(on_delete=models.CASCADE, to='recipe_mgr.FoodTag'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dish',
            name='dish_type',
            field=models.ForeignKey(on_delete=models.CASCADE, to='recipe_mgr.DishType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dish',
            name='meal_slot',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='dishes', to='planning_mgr.MealSlot'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dish',
            name='recipes',
            field=models.ManyToManyField(through='planning_mgr.DishRecipe', to='recipe_mgr.Recipe'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='day',
            name='planning',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='days', to='planning_mgr.MetaPlanning'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='day',
            name='shopping_list',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, to='shopping_mgr.ShoppingList', null=True, related_name='days'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='day',
            name='user',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='days', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='day',
            unique_together=set([('date', 'user')]),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('shopping_mgr', '0001_initial'),
        ('location_mgr', '0001_initial'),
        ('recipe_mgr', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='reciperating',
            name='moderator',
            field=models.ForeignKey(on_delete=models.CASCADE, null=True, to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='reciperating',
            name='recipe',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='ratings', to='recipe_mgr.Recipe'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='reciperating',
            name='user',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='recipe_ratings', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='reciperating',
            unique_together=set([('recipe', 'user')]),
        ),
        migrations.AddField(
            model_name='recipeinstruction',
            name='recipe',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='instructions', to='recipe_mgr.Recipe'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='recipedishtype',
            name='dish_type',
            field=models.ForeignKey(on_delete=models.CASCADE, to='recipe_mgr.DishType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='recipedishtype',
            name='recipe',
            field=models.ForeignKey(on_delete=models.CASCADE, to='recipe_mgr.Recipe'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='recipedishtype',
            unique_together=set([('recipe', 'dish_type')]),
        ),
        migrations.AddField(
            model_name='recipe',
            name='author',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='written_recipes', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='recipe',
            name='dish_types',
            field=models.ManyToManyField(through='recipe_mgr.RecipeDishType', to='recipe_mgr.DishType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='recipe',
            name='origin',
            field=models.ForeignKey(on_delete=models.CASCADE, blank=True, to='location_mgr.Location', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='recipe',
            name='publisher',
            field=models.ForeignKey(on_delete=models.CASCADE, default=None, to=settings.AUTH_USER_MODEL, null=True, related_name='publications'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='recipe',
            name='tags',
            field=models.ManyToManyField(to='recipe_mgr.RecipeTag'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='recipe',
            name='ustensils',
            field=models.ManyToManyField(to='recipe_mgr.Ustensil'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ingredient',
            name='cooking_method',
            field=models.ForeignKey(on_delete=models.CASCADE, to='recipe_mgr.CookingMethod'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ingredient',
            name='default_conversion',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='ingredients', to='recipe_mgr.FoodConversion'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ingredient',
            name='food',
            field=models.ForeignKey(on_delete=models.CASCADE, to='recipe_mgr.Food'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ingredient',
            name='raw_state',
            field=models.ForeignKey(on_delete=models.CASCADE, to='recipe_mgr.RawState'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='ingredient',
            name='recipe',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='ingredients', to='recipe_mgr.Recipe'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='foodtype',
            name='source',
            field=models.ForeignKey(on_delete=models.CASCADE, blank=True, to='recipe_mgr.FoodSource', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='foodtagset',
            name='food',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='tagsets', to='recipe_mgr.Food'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='foodtagset',
            name='tag',
            field=models.ForeignKey(on_delete=models.CASCADE, to='recipe_mgr.FoodTag'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='foodtag',
            name='children',
            field=models.ManyToManyField(related_name='parents', to='recipe_mgr.FoodTag'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='foodtag',
            name='foods',
            field=models.ManyToManyField(through='recipe_mgr.FoodTagSet', related_name='food_tags', to='recipe_mgr.Food'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='foodseasonality',
            name='food',
            field=models.ForeignKey(on_delete=models.CASCADE, unique=True, to='recipe_mgr.Food', related_name='season'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='foodconversion',
            name='food',
            field=models.ForeignKey(on_delete=models.CASCADE, editable=False, to='recipe_mgr.Food', related_name='conversions'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='food',
            name='default_conversion',
            field=models.ForeignKey(on_delete=models.CASCADE, default=None, to='recipe_mgr.FoodConversion', null=True, related_name='default_foods'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='food',
            name='default_cooking_method',
            field=models.ForeignKey(on_delete=models.CASCADE, default=None, to='recipe_mgr.CookingMethod', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='food',
            name='default_raw_state',
            field=models.ForeignKey(on_delete=models.CASCADE, default=None, to='recipe_mgr.RawState', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='food',
            name='food_source',
            field=models.ForeignKey(on_delete=models.CASCADE, blank=True, to='recipe_mgr.FoodSource', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='food',
            name='parent',
            field=models.ForeignKey(on_delete=models.CASCADE, blank=True, to='recipe_mgr.Food', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='food',
            name='shopping_category',
            field=models.ForeignKey(on_delete=models.CASCADE, to='shopping_mgr.ShoppingCategory'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='food',
            name='tags',
            field=models.ManyToManyField(through='recipe_mgr.FoodTagSet', to='recipe_mgr.FoodTag'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='food',
            name='type',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='foods', to='recipe_mgr.FoodType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dishtypeunion',
            name='master_dish_type',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='unions_as_master', to='recipe_mgr.DishType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dishtypeunion',
            name='sub_dish_type',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='unions_as_sub', to='recipe_mgr.DishType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dishtypeaggregation',
            name='master_dish_type',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='aggregations_as_master', to='recipe_mgr.DishType'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='dishtypeaggregation',
            name='sub_dish_type',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='aggregations_as_sub', to='recipe_mgr.DishType'),
            preserve_default=True,
        ),
    ]

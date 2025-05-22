# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('diet_mgr', '0001_initial'),
        ('recipe_mgr', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='userdietparameter',
            name='user',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='diet_parameters', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='userdietparameter',
            unique_together=set([('user', 'name')]),
        ),
        migrations.AddField(
            model_name='diet',
            name='excluded_food_tags',
            field=models.ManyToManyField(related_name='diets_with_exclusion', to='recipe_mgr.FoodTag'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='diet',
            name='included_food_tags',
            field=models.ManyToManyField(related_name='diets_with_inclusion', to='recipe_mgr.FoodTag'),
            preserve_default=True,
        ),
    ]

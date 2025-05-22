# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('profile_mgr', '0001_initial'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipe_mgr', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='taste',
            name='food_tag',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='tastes', to='recipe_mgr.FoodTag'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='taste',
            name='profile',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='tastes', to='profile_mgr.Profile'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='taste',
            unique_together=set([('profile', 'food_tag')]),
        ),
        migrations.AddField(
            model_name='restrictedfood',
            name='food_tag',
            field=models.ForeignKey(on_delete=models.CASCADE, to='recipe_mgr.FoodTag'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='restrictedfood',
            name='profile',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='restrictions', to='profile_mgr.Profile'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='restrictedfood',
            unique_together=set([('profile', 'food_tag')]),
        ),
        migrations.AddField(
            model_name='recipedislike',
            name='profile',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='recipe_dislikes', to='profile_mgr.Profile'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='recipedislike',
            name='recipe',
            field=models.ForeignKey(on_delete=models.CASCADE, to='recipe_mgr.Recipe'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='recipedislike',
            unique_together=set([('profile', 'recipe')]),
        ),
        migrations.AddField(
            model_name='profilevalue',
            name='metric',
            field=models.ForeignKey(on_delete=models.CASCADE, to='profile_mgr.ProfileMetric'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='profilevalue',
            name='profile',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='values', to='profile_mgr.Profile'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='profile',
            name='creator',
            field=models.ForeignKey(on_delete=models.CASCADE, default=None, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
    ]

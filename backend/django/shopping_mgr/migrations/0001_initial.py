# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import common.model
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipe_mgr', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='ShoppingCategory',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=100)),
            ],
            options={
            },
            bases=(common.model.NamedModel, models.Model),
        ),
        migrations.CreateModel(
            name='ShoppingItem',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('grams', models.FloatField()),
                ('checked', models.BooleanField(default=True)),
                ('forced_quantity', models.TextField(null=True)),
                ('food', models.ForeignKey(on_delete=models.CASCADE, to='recipe_mgr.Food')),
                ('raw_state', models.ForeignKey(on_delete=models.CASCADE, to='recipe_mgr.RawState')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ShoppingList',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('user', models.ForeignKey(on_delete=models.CASCADE, related_name='shopping_lists', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TextShoppingItem',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('text', models.TextField()),
                ('shopping_category', models.ForeignKey(on_delete=models.CASCADE, null=True, to='shopping_mgr.ShoppingCategory')),
                ('shopping_list', models.ForeignKey(on_delete=models.CASCADE, related_name='additional_items', to='shopping_mgr.ShoppingList')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='shoppingitem',
            name='shopping_list',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='items', to='shopping_mgr.ShoppingList'),
            preserve_default=True,
        ),
    ]

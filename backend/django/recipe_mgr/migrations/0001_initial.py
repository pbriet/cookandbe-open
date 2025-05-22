# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
import common.model


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='CookingMethod',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=200)),
            ],
            options={
            },
            bases=(common.model.NamedModel, models.Model),
        ),
        migrations.CreateModel(
            name='DishType',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=64)),
                ('system', models.BooleanField(default=False)),
                ('standard_calories', models.IntegerField(null=True)),
            ],
            options={
            },
            bases=(common.model.NamedModel, models.Model),
        ),
        migrations.CreateModel(
            name='DishTypeAggregation',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='DishTypeUnion',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Food',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=150)),
                ('full_name', models.CharField(max_length=200)),
                ('enabled', models.BooleanField(default=True)),
                ('original', models.CharField(blank=True, null=True, max_length=50)),
                ('internal', models.BooleanField(default=False)),
                ('has_nutrients', models.BooleanField(default=True)),
            ],
            options={
            },
            bases=(common.model.NamedModel, models.Model),
        ),
        migrations.CreateModel(
            name='FoodConversion',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('unit', models.CharField(max_length=200)),
                ('unit_plural', models.CharField(max_length=200)),
                ('value', models.FloatField()),
                ('shopping_compatible', models.BooleanField(default=True)),
                ('splittable', models.BooleanField(default=True)),
                ('loss_coeff', models.FloatField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)], default=0)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FoodSeasonality',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('start_month', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(12)])),
                ('end_month', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(12)])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FoodSource',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=30)),
                ('copyright_info', models.TextField()),
            ],
            options={
            },
            bases=(common.model.NamedModel, models.Model),
        ),
        migrations.CreateModel(
            name='FoodTag',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('url_key', models.CharField(db_index=True, blank=True, max_length=500)),
                ('name', models.CharField(max_length=200)),
                ('can_be_disliked', models.BooleanField(default=True)),
                ('photo', models.ImageField(upload_to='food_tag/photo', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(common.model.NamedModel, models.Model),
        ),
        migrations.CreateModel(
            name='FoodTagSet',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('component', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FoodType',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=200)),
                ('hierarchy_code', models.CharField(blank=True, null=True, max_length=10)),
                ('is_fresh', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(common.model.NamedModel, models.Model),
        ),
        migrations.CreateModel(
            name='Ingredient',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('grams', models.FloatField(validators=[django.core.validators.MinValueValidator(0)])),
                ('previously_cooked', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RawState',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=50)),
            ],
            options={
            },
            bases=(common.model.NamedModel, models.Model),
        ),
        migrations.CreateModel(
            name='Recipe',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('url_key', models.CharField(db_index=True, blank=True, max_length=500)),
                ('name', models.CharField(max_length=200)),
                ('price', models.IntegerField()),
                ('prep_minutes', models.IntegerField(default=15)),
                ('rest_minutes', models.IntegerField(default=0)),
                ('cook_minutes', models.IntegerField(default=15)),
                ('difficulty', models.IntegerField()),
                ('copyright_free', models.BooleanField(default=False)),
                ('source_url', models.CharField(blank=True, null=True, max_length=200)),
                ('nb_people', models.IntegerField()),
                ('internal', models.BooleanField(default=False)),
                ('summary', models.TextField(null=True)),
                ('photo', models.ImageField(upload_to='recipe/photo', null=True)),
                ('auto_photo', models.BooleanField(default=True)),
                ('avg_rating', models.FloatField(null=True)),
                ('nb_ratings', models.IntegerField(default=0)),
                ('status', models.IntegerField(default=0)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('modification_date', models.DateTimeField(auto_now=True)),
                ('publication_date', models.DateTimeField(null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(common.model.NamedModel, models.Model),
        ),
        migrations.CreateModel(
            name='RecipeDishType',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RecipeInstruction',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('text', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RecipeRating',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('rating', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(5)])),
                ('comment', models.TextField(blank=True, null=True)),
                ('moderated_at', models.DateTimeField(blank=True, null=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='RecipeTag',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('url_key', models.CharField(db_index=True, blank=True, max_length=500)),
                ('name', models.CharField(max_length=200)),
                ('parent', models.ForeignKey(on_delete=models.CASCADE, blank=True, to='recipe_mgr.RecipeTag', null=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(common.model.NamedModel, models.Model),
        ),
        migrations.CreateModel(
            name='Ustensil',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=200)),
                ('default_check', models.BooleanField(default=False)),
            ],
            options={
            },
            bases=(common.model.NamedModel, models.Model),
        ),
        migrations.CreateModel(
            name='UstensilCategory',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=64)),
            ],
            options={
            },
            bases=(common.model.NamedModel, models.Model),
        ),
        migrations.AddField(
            model_name='ustensil',
            name='category',
            field=models.ForeignKey(on_delete=models.CASCADE, to='recipe_mgr.UstensilCategory'),
            preserve_default=True,
        ),
    ]

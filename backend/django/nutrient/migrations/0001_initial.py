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
            name='CookingMethodEffect',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('weight_ratio', models.FloatField(validators=[django.core.validators.MinValueValidator(0)])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='FoodNutrient',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('amount_per_gram', models.FloatField()),
                ('std_err', models.FloatField(blank=True, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Nutrient',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('key', models.CharField(max_length=50)),
                ('name', models.CharField(max_length=200)),
                ('short_name', models.CharField(max_length=50)),
                ('unit', models.CharField(max_length=20)),
                ('infoods_tagname', models.CharField(max_length=10)),
                ('ciqual_id', models.IntegerField(blank=True, null=True)),
                ('cnf_id', models.IntegerField(blank=True, null=True)),
                ('enabled', models.BooleanField(default=True)),
            ],
            options={
            },
            bases=(common.model.NamedModel, models.Model),
        ),
        migrations.CreateModel(
            name='NutrientCookAlteration',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('ratio', models.FloatField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)])),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='NutrientRawStateAlteration',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('ratio', models.FloatField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(1)])),
                ('nutrient', models.ForeignKey(on_delete=models.CASCADE, to='nutrient.Nutrient')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Diet',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('key', models.CharField(max_length=32)),
                ('title', models.CharField(max_length=64)),
                ('email_title', models.CharField(max_length=64)),
                ('description', models.CharField(max_length=512)),
                ('default_display', models.BooleanField(default=True)),
                ('enabled', models.BooleanField(default=False)),
                ('min_subscription_level', models.IntegerField(default=0)),
                ('has_diagnostic', models.BooleanField(default=False)),
                ('free_trial_days', models.IntegerField(default=7)),
                ('url_key', models.CharField(unique=True, db_index=True, max_length=500)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserDietParameter',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=16)),
                ('float_value', models.FloatField(null=True)),
                ('string_value', models.CharField(null=True, max_length=64)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]

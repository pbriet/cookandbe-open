# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipe_mgr', '0002_auto_20150609_1214'),
    ]

    operations = [
        migrations.CreateModel(
            name='FoodStock',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, primary_key=True, verbose_name='ID')),
                ('grams', models.FloatField()),
                ('expiry', models.DateField(default=None, null=True)),
                ('food', models.ForeignKey(on_delete=models.CASCADE, to='recipe_mgr.Food')),
                ('user', models.ForeignKey(on_delete=models.CASCADE, to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]

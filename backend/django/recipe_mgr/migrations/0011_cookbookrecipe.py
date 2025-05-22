# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('recipe_mgr', '0010_auto_20150903_1819'),
    ]

    operations = [
        migrations.CreateModel(
            name='CookbookRecipe',
            fields=[
                ('id', models.AutoField(auto_created=True, serialize=False, verbose_name='ID', primary_key=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('recipe', models.ForeignKey(on_delete=models.CASCADE, to='recipe_mgr.Recipe')),
                ('user', models.ForeignKey(on_delete=models.CASCADE, to=settings.AUTH_USER_MODEL, related_name='cookbook_recipes')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]

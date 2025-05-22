# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('recipe_mgr', '0011_cookbookrecipe'),
    ]

    operations = [
        migrations.AlterField(
            model_name='cookbookrecipe',
            name='recipe',
            field=models.ForeignKey(on_delete=models.CASCADE, to='recipe_mgr.Recipe', related_name='cookbook_selections'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='cookbookrecipe',
            unique_together=set([('user', 'recipe')]),
        ),
    ]

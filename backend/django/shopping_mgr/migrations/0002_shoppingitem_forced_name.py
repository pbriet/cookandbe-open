# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shopping_mgr', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='shoppingitem',
            name='forced_name',
            field=models.TextField(null=True),
            preserve_default=True,
        ),
    ]

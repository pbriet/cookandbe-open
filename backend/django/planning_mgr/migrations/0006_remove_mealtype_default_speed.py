# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planning_mgr', '0005_auto_20150707_1227'),
    ]

    operations = [
        migrations.RemoveField(
            model_name='mealtype',
            name='default_speed',
        ),
    ]

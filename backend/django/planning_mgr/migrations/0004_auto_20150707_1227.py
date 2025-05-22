# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('planning_mgr', '0003_auto_20150624_1527'),
    ]

    operations = [
        migrations.AddField(
            model_name='mealdishoption',
            name='min_budget_check',
            field=models.IntegerField(default=2, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='mealdishoption',
            name='min_speed_check',
            field=models.IntegerField(default=2, null=True),
            preserve_default=True,
        ),
        migrations.RemoveField(
            model_name='mealdishoption',
            name='default_check'
        )
    ]

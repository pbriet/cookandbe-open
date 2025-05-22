# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('location_mgr', '0002_address'),
        ('user_mgr', '0006_auto_20150803_1242'),
    ]

    operations = [
        migrations.AddField(
            model_name='baseuser',
            name='main_address',
            field=models.ForeignKey(on_delete=django.db.models.deletion.SET_NULL, null=True, related_name='user', to='location_mgr.Address', blank=True),
            preserve_default=True,
        ),
    ]

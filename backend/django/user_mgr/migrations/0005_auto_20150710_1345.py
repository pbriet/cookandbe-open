# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_mgr', '0004_auto_20150710_1123'),
    ]

    operations = [
        migrations.AlterField(
            model_name='configstage',
            name='express_description',
            field=models.TextField(default='default'),
            preserve_default=False,
        ),
    ]

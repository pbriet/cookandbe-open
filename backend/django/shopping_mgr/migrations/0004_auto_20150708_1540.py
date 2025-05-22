# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('shopping_mgr', '0003_auto_20150703_1942'),
    ]

    operations = [
        migrations.RenameField(
            model_name='shoppingitem',
            old_name='checked',
            new_name='got_it',
        ),
    ]

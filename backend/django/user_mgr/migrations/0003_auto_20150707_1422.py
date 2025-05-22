# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_mgr', '0002_baseuser_mail_daily'),
    ]

    operations = [
        migrations.AddField(
            model_name='user',
            name='budget',
            field=models.IntegerField(default=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='fish_level',
            field=models.IntegerField(default=2),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='meat_level',
            field=models.IntegerField(default=2),
            preserve_default=True,
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('user_mgr', '0007_baseuser_main_address'),
    ]

    operations = [
        migrations.AlterField(
            model_name='baseuser',
            name='email',
            field=models.EmailField(blank=True, max_length=254, verbose_name='email address', unique=True),
        ),
        migrations.AlterField(
            model_name='baseuser',
            name='last_login',
            field=models.DateTimeField(blank=True, null=True, verbose_name='last login'),
        ),
        migrations.AlterField(
            model_name='invitation',
            name='email',
            field=models.EmailField(max_length=254, unique=True),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('newsletters', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='newsletter',
            name='sent_by',
            field=models.ForeignKey(on_delete=models.CASCADE, null=True, to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]

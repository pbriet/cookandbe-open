# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('paybox', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='temporaryoffer',
            name='user',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='temporary_offers', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='subscription',
            name='user',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='subscriptions', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
    ]

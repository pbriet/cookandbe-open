# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('discussion', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='publication',
            name='author',
            field=models.ForeignKey(on_delete=models.CASCADE, default=None, to=settings.AUTH_USER_MODEL, null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='message',
            name='author',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='messages', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='message',
            name='discussion',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='messages', to='discussion.Discussion'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='discussion',
            name='dietician',
            field=models.ForeignKey(on_delete=models.CASCADE, default=None, to=settings.AUTH_USER_MODEL, null=True, related_name='patient_discussions'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='discussion',
            name='owner',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='discussions', to=settings.AUTH_USER_MODEL),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='discussion',
            name='publication',
            field=models.OneToOneField(on_delete=models.CASCADE, default=None, to='discussion.Publication', null=True, related_name='discussion'),
            preserve_default=True,
        ),
    ]

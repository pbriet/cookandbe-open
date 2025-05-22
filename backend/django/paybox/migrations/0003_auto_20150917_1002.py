# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
        ('paybox', '0002_auto_20150609_1214'),
    ]

    operations = [
        migrations.CreateModel(
            name='UserSpecialOffer',
            fields=[
                ('id', models.AutoField(primary_key=True, verbose_name='ID', serialize=False, auto_created=True)),
                ('discount', models.IntegerField()),
                ('until', models.DateTimeField()),
                ('user', models.ForeignKey(on_delete=models.CASCADE, related_name='special_offers', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.RemoveField(
            model_name='temporaryoffer',
            name='user',
        ),
        migrations.DeleteModel(
            name='TemporaryOffer',
        ),
    ]

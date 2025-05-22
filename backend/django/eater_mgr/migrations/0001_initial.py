# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings


class Migration(migrations.Migration):

    dependencies = [
        ('profile_mgr', '0002_auto_20150609_1214'),
        migrations.swappable_dependency(settings.AUTH_USER_MODEL),
    ]

    operations = [
        migrations.CreateModel(
            name='Eater',
            fields=[
                ('id', models.AutoField(serialize=False, auto_created=True, verbose_name='ID', primary_key=True)),
                ('regular', models.BooleanField(default=True)),
                ('profile', models.ForeignKey(on_delete=models.CASCADE, to='profile_mgr.Profile')),
                ('user', models.ForeignKey(on_delete=models.CASCADE, related_name='eaters', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]

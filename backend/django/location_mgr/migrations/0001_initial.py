# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators
import common.model


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Location',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(max_length=200)),
                ('parent', models.ForeignKey(on_delete=models.CASCADE, blank=True, to='location_mgr.Location', null=True)),
            ],
            options={
            },
            bases=(common.model.NamedModel, models.Model),
        ),
    ]

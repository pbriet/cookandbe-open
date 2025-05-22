# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import common.model


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='FoodProvider',
            fields=[
                ('id', models.AutoField(primary_key=True, auto_created=True, serialize=False, verbose_name='ID')),
                ('name', models.CharField(max_length=64)),
            ],
            options={
            },
            bases=(common.model.NamedModel, models.Model),
        ),
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Newsletter',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('sent_at', models.DateTimeField(null=True)),
                ('subject', models.CharField(max_length=200)),
                ('content', models.TextField()),
                ('template_name', models.CharField(null=True, max_length=100)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]

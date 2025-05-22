# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('location_mgr', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='Address',
            fields=[
                ('id', models.AutoField(auto_created=True, verbose_name='ID', serialize=False, primary_key=True)),
                ('postal_code', models.CharField(max_length=16, null=True, blank=True)),
                ('country', models.ForeignKey(on_delete=models.CASCADE, to='location_mgr.Location', blank=True, null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]

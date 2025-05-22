# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Discussion',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('title', models.CharField(max_length=150)),
                ('close_date', models.DateTimeField(null=True, default=None)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('last_date', models.DateTimeField(null=True, default=None)),
                ('owner_read_date', models.DateTimeField(null=True, default=None)),
                ('dietician_read_date', models.DateTimeField(null=True, default=None)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Message',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('content', models.TextField()),
                ('date', models.DateTimeField(auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Publication',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('url_key', models.CharField(db_index=True, blank=True, max_length=500)),
                ('question', models.TextField(null=True, default=None)),
                ('response', models.TextField(null=True, default=None)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
                ('public', models.BooleanField(default=False)),
                ('user_sex', models.BooleanField(default=True)),
                ('user_date', models.DateField()),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
    ]

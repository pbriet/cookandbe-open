# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='AbCampaign',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('key', models.CharField(unique=True, db_index=True, max_length=30)),
                ('description', models.TextField()),
                ('created_at', models.DateTimeField(auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AbChoice',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('unique_id', models.CharField(max_length=80)),
                ('campaign', models.ForeignKey(on_delete=models.CASCADE, related_name='choices', to='abtest.AbCampaign')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AbOption',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('key', models.CharField(max_length=30)),
                ('campaign', models.ForeignKey(on_delete=models.CASCADE, related_name='options', to='abtest.AbCampaign')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='AbRecord',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('objective', models.CharField(max_length=30)),
                ('choice', models.ForeignKey(on_delete=models.CASCADE, related_name='records', to='abtest.AbChoice')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='abchoice',
            name='option',
            field=models.ForeignKey(on_delete=models.CASCADE, to='abtest.AbOption'),
            preserve_default=True,
        ),
    ]

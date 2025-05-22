# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
import django.core.validators


class Migration(migrations.Migration):

    dependencies = [
    ]

    operations = [
        migrations.CreateModel(
            name='Subscription',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('level', models.IntegerField(validators=[django.core.validators.MinValueValidator(1), django.core.validators.MaxValueValidator(2)])),
                ('start_date', models.DateField()),
                ('end_date', models.DateField()),
                ('nb_months', models.IntegerField(default=0)),
                ('nb_days', models.IntegerField(default=0)),
                ('trial_period_end', models.DateField()),
                ('total_amount', models.IntegerField()),
                ('enabled', models.BooleanField(default=False)),
                ('cancelled', models.BooleanField(default=False)),
                ('discount', models.IntegerField(validators=[django.core.validators.MinValueValidator(0), django.core.validators.MaxValueValidator(75)], null=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='TemporaryOffer',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('discount', models.IntegerField()),
                ('until', models.DateTimeField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Transaction',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('created_at', models.DateTimeField(auto_now_add=True)),
                ('ref', models.CharField(unique=True, max_length=128)),
                ('transaction_id', models.IntegerField(null=True)),
                ('payment_type', models.CharField(null=True, max_length=30)),
                ('price', models.IntegerField()),
                ('ip', models.CharField(max_length=50)),
                ('authorization_code', models.CharField(null=True, max_length=100)),
                ('concluded_at', models.DateTimeField(blank=True, null=True)),
                ('error_code', models.IntegerField(null=True)),
                ('status', models.IntegerField()),
                ('subscription', models.ForeignKey(on_delete=models.CASCADE, related_name='transactions', to='paybox.Subscription')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
    ]

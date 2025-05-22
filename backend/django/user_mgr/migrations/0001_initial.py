# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations
from django.conf import settings
import django.db.models.deletion
import common.model
import django.utils.timezone


class Migration(migrations.Migration):

    dependencies = [
        ('profile_mgr', '0001_initial'),
        ('diet_mgr', '0001_initial'),
        ('planning_mgr', '0001_initial'),
        ('recipe_mgr', '0001_initial'),
    ]

    operations = [
        migrations.CreateModel(
            name='BaseUser',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('password', models.CharField(verbose_name='password', max_length=128)),
                ('last_login', models.DateTimeField(verbose_name='last login', default=django.utils.timezone.now)),
                ('first_name', models.CharField(verbose_name='first name', blank=True, max_length=30)),
                ('last_name', models.CharField(verbose_name='last name', blank=True, max_length=30)),
                ('email', models.EmailField(unique=True, blank=True, verbose_name='email address', max_length=75)),
                ('date_joined', models.DateTimeField(verbose_name='date joined', default=django.utils.timezone.now)),
                ('facebook_id', models.CharField(blank=True, max_length=30)),
                ('mail_notifications', models.BooleanField(default=True)),
                ('mail_newsletter', models.BooleanField(default=True)),
            ],
            options={
                'abstract': False,
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='User',
            fields=[
                ('baseuser_ptr', models.OneToOneField(on_delete=models.CASCADE, serialize=False, primary_key=True, parent_link=True, to='user_mgr.BaseUser', auto_created=True)),
                ('shopping_day', models.IntegerField(default=6)),
                ('diet_changed_at', models.DateTimeField(verbose_name='date joined', blank=True, null=True)),
                ('enabled', models.BooleanField(default=True)),
                ('subscription_level', models.IntegerField(default=0)),
            ],
            options={
                'verbose_name': 'user',
                'verbose_name_plural': 'users',
            },
            bases=('user_mgr.baseuser',),
        ),
        migrations.CreateModel(
            name='BaseUserRole',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('creation_date', models.DateTimeField(auto_now_add=True)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ConfigStage',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.TextField()),
                ('description', models.TextField()),
                ('key', models.CharField(max_length=20)),
                ('order', models.IntegerField()),
                ('validity_days', models.IntegerField(blank=True, null=True, default=None)),
            ],
            options={
            },
            bases=(common.model.NamedModel, models.Model),
        ),
        migrations.CreateModel(
            name='ConfigStageCompletion',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('stage', models.ForeignKey(on_delete=models.CASCADE, to='user_mgr.ConfigStage')),
                ('user', models.ForeignKey(on_delete=models.CASCADE, related_name='config_stage_completions', to=settings.AUTH_USER_MODEL)),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='Invitation',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('email', models.EmailField(unique=True, max_length=75)),
                ('sent_at', models.DateTimeField(auto_now=True)),
                ('key', models.CharField(unique=True, max_length=32)),
                ('first_name', models.CharField(null=True, max_length=30)),
                ('last_name', models.CharField(null=True, max_length=30)),
                ('diet', models.ForeignKey(on_delete=models.CASCADE, null=True, to='diet_mgr.Diet')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='ProUser',
            fields=[
                ('baseuser_ptr', models.OneToOneField(on_delete=models.CASCADE, serialize=False, primary_key=True, parent_link=True, to='user_mgr.BaseUser', auto_created=True)),
            ],
            options={
                'abstract': False,
            },
            bases=('user_mgr.baseuser',),
        ),
        migrations.CreateModel(
            name='Role',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('name', models.CharField(unique=True, blank=True, max_length=32)),
                ('description', models.TextField()),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.CreateModel(
            name='UserOperation',
            fields=[
                ('id', models.AutoField(serialize=False, verbose_name='ID', primary_key=True, auto_created=True)),
                ('date', models.DateTimeField(auto_now_add=True)),
                ('operation', models.CharField(max_length=16)),
                ('ip', models.CharField(max_length=32)),
                ('used', models.BooleanField(default=False)),
                ('key', models.CharField(unique=True, max_length=32)),
                ('user', models.ForeignKey(on_delete=models.CASCADE, to='user_mgr.BaseUser')),
            ],
            options={
            },
            bases=(models.Model,),
        ),
        migrations.AddField(
            model_name='invitation',
            name='sent_by',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='sent_invitations', to='user_mgr.BaseUser'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='configstagecompletion',
            unique_together=set([('user', 'stage')]),
        ),
        migrations.AddField(
            model_name='baseuserrole',
            name='created_by',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='promotions', to='user_mgr.BaseUser'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='baseuserrole',
            name='role',
            field=models.ForeignKey(on_delete=models.CASCADE, to='user_mgr.Role'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='baseuserrole',
            name='user',
            field=models.ForeignKey(on_delete=models.CASCADE, related_name='user_roles', to='user_mgr.BaseUser'),
            preserve_default=True,
        ),
        migrations.AlterUniqueTogether(
            name='baseuserrole',
            unique_together=set([('user', 'role')]),
        ),
        migrations.AddField(
            model_name='user',
            name='completed_stages',
            field=models.ManyToManyField(through='user_mgr.ConfigStageCompletion', to='user_mgr.ConfigStage'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='diet',
            field=models.ForeignKey(on_delete=models.CASCADE, null=True, to='diet_mgr.Diet'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='main_profile',
            field=models.ForeignKey(default=None, on_delete=django.db.models.deletion.SET_NULL, to='profile_mgr.Profile', null=True),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='meta_planning',
            field=models.ForeignKey(blank=True, on_delete=django.db.models.deletion.SET_NULL, to='planning_mgr.MetaPlanning', null=True, related_name='+'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='pro',
            field=models.ForeignKey(on_delete=models.CASCADE, to='user_mgr.ProUser', null=True, related_name='patients'),
            preserve_default=True,
        ),
        migrations.AddField(
            model_name='user',
            name='ustensils',
            field=models.ManyToManyField(to='recipe_mgr.Ustensil'),
            preserve_default=True,
        ),
    ]

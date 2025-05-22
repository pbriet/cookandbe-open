# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    dependencies = [
        ('abtest', '0002_abchoice_user'),
    ]
    
    def add_cookbook_ab_test(apps, schema_editor):
        AbCampaign    = apps.get_model("abtest", "AbCampaign")
        AbOption    = apps.get_model("abtest", "AbOption")
        
        campaign = AbCampaign.objects.create(key="cookbook_tab_name", description="Cookbook tab name")
        AbOption.objects.create(campaign=campaign, key="my_cookbook")
        AbOption.objects.create(campaign=campaign, key="my_recipes")

    operations = [
        migrations.RunPython(add_cookbook_ab_test)
    ]

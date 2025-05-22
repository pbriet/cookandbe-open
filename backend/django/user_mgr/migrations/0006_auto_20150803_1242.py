# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    def split_config_stages(apps, schema_editor):
         ConfigStage = apps.get_model("user_mgr", "ConfigStage")
         ConfigStageCompletion = apps.get_model("user_mgr", "ConfigStageCompletion")
         User = apps.get_model("user_mgr", "User")
         
         
         other_stage = ConfigStage.objects.get(key="other")
         
         equipment_stage = ConfigStage.objects.create(key="equipment",
                                                      description="Quels ustensiles j'ai en cuisine ?",
                                                      express_description="Four, hachoir, ...",
                                                      name="Mes équipements",
                                                      order=7)
         
         other_stage.description = "Mon budget, ma quantité de poisson et viande, ..."
         other_stage.save()
                                                      
         cs_dict = {}
         
         for cs in ConfigStage.objects.all():
             cs_dict[cs.key] = cs
         
         user_profile = cs_dict["user_profile"]
         tastes = cs_dict["tastes"]
         attendance = cs_dict["attendance"]
         equipment = cs_dict["equipment"]
         habits = cs_dict["habits"]
         family = cs_dict["family"]
         
         
         user_profile.name = "Mes caractéristiques"
         user_profile.save()
         habits.name = "Mes repas"
         habits.save()
         attendance.name = "Mon emploi du temps"
         attendance.save()
         family.name = "Mon foyer"
         family.express_description = "Qui mange avec moi"
         family.save()
         tastes.name = "Mes goûts"
         tastes.express_description = "Ce que j'aime"
         tastes.save()
         
         for user in User.objects.all():
             ConfigStageCompletion.objects.create(user=user, stage=equipment_stage)
         

    dependencies = [
        ('user_mgr', '0005_auto_20150710_1345'),
    ]

    operations = [
        # migrations.RunPython(split_config_stages)
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import models, migrations


class Migration(migrations.Migration):

    def update_config_stages(apps, schema_editor):
         ConfigStage = apps.get_model("user_mgr", "ConfigStage")
         
         cs_dict = {}
         
         for cs in ConfigStage.objects.all():
             cs_dict[cs.key] = cs
         
         user_profile = cs_dict["user_profile"]
         tastes = cs_dict["tastes"]
         meal_sharing = cs_dict["meal_sharing"]
         equipment = cs_dict["equipment"]
         attendance = cs_dict["attendance"]
         habits = cs_dict["habits"]
         family = cs_dict["family"]
         
         meal_sharing.delete()
         
         user_profile.order = 1
         user_profile.save()
         attendance.order = 2
         attendance.save()
         habits.order = 3
         habits.save()
         family.order = 4
         family.save()
         tastes.order = 5
         tastes.save()
         equipment.order = 6
         equipment.save()
         
         STAGES_DATA = {
             "tastes": ("tastes", "Vos goûts", "Ce que vous aimez", None),
             "user_profile": ("user_profile", "Votre profil", "Age, taille, poids, ...", None),
             "attendance": ("attendance", "Emploi du temps", "Quand et où ?", None),
             "habits": ("habits", "Vos repas", "Composition et temps", None),
             "family": ("family", "Votre foyer", "Qui mange avec vous", None),
             "equipment": ("other", "Divers", "Budget, équipement, ...", "Renseignez votre budget, vos habitudes en viande/poisson et vos équipements")
         }
         
         for key, data in STAGES_DATA.items():
             new_key, title, express, full = data
             stage = cs_dict[key]
             
             stage.name = title
             stage.key = new_key
             if full is not None:
                 stage.description = full
             stage.express_description = express
             stage.save()
         
         

    dependencies = [
        ('user_mgr', '0003_auto_20150707_1422'),
    ]

    operations = [
        migrations.AddField(
            model_name='configstage',
            name='express_description',
            field=models.TextField(null=True)
        ),
        # migrations.RunPython(update_config_stages)
    ]

# -*- coding: utf-8 -*-
from __future__ import unicode_literals

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('recipe_mgr', '0013_vegan_specific_tags'),
    ]

    def fix_bug_personal_recipe_in_cookbook(apps, schema_editor):
        """
        Removing personal recipes that have been added in cookbooks
        """
        CookbookRecipe = apps.get_model("recipe_mgr", "CookbookRecipe")
        
        for cookbook_recipe in CookbookRecipe.objects.select_related("recipe").all():
            
            if cookbook_recipe.recipe.author_id == cookbook_recipe.user_id:
                # Bug
                print("Removing cookbook recipe : User_id = %s, recipe = %s" % (cookbook_recipe.user_id, cookbook_recipe.recipe.name))
                cookbook_recipe.delete()
            
    operations = [
        migrations.RunPython(fix_bug_personal_recipe_in_cookbook),
    ]

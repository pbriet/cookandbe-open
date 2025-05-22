#!/usr/bin/env python
from bases.op_base      import DjangoMuninScript
from optalim.mongo      import Mongo
from recipe_mgr.models  import CookbookRecipe, Recipe, RecipeRating

class RecipeActivity(DjangoMuninScript):
    def apply_config(self):
        print("graph_title Recipes activity")
        print('graph_category recipes')
        print("nb_cookbooks.draw LINE1")
        print("nb_cookbooks.label Recipes in cookbooks")
        print("nb_ratings.draw LINE1")
        print("nb_ratings.label Recipe ratings")
        print("nb_personal_recipes.draw LINE1")
        print("nb_personal_recipes.label Personal recipes")
        print("nb_public_recipes.draw LINE1")
        print("nb_public_recipes.label Public recipes")



    def apply_values(self):
        nb_public_recipes = Recipe.objects.filter(status=Recipe.STATUS_PUBLISHED, internal=False).count()
        print("nb_public_recipes.value %i" % nb_public_recipes)
        nb_personal_recipes = Recipe.objects.filter(status=Recipe.STATUS_VALIDATED, author__user_roles=None, internal=False).count()
        print("nb_personal_recipes.value %i" % nb_personal_recipes)
        nb_cookbooks = CookbookRecipe.objects.count()
        print("nb_cookbooks.value %i" % nb_cookbooks)
        nb_ratings = RecipeRating.objects.count()
        print("nb_ratings.value %i" % nb_ratings)

RecipeActivity().apply()
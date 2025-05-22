from django.core.management.base    import BaseCommand
from collections                    import defaultdict
from recipe_mgr.models              import CookbookRecipe, Recipe
from user_mgr.models                import User
import numpy

class Command(BaseCommand):
    args = ''
    help = 'Give stats on personal recipes/favorites/...'

    def handle(self, *args, **options):
        
        # Personal recipes
        personal_recipes = Recipe.objects.filter(status=Recipe.STATUS_VALIDATED, author__user_roles=None, internal=False)
        
        nb_users = User.objects.count()
        
        print("* personal recipes : ", len(personal_recipes), " (avg per user : ", float(len(personal_recipes)) / nb_users)
        
        
        # Favorite recipes
        cb_recipes = list(CookbookRecipe.objects.select_related('recipe').all())
        favorite_recipes = defaultdict(int)
        favorite_by_users = defaultdict(int)
        recipe_by_id = {}
        
        for cbr in cb_recipes:
            favorite_recipes[cbr.recipe_id] += 1
            favorite_by_users[cbr.user_id] += 1
            recipe_by_id[cbr.recipe_id] = cbr.recipe
        print("* favorite recipes : ", len(cb_recipes), " (avg per user : ", float(len(cb_recipes)) / nb_users)
        print("* %i users using it, with an average of %s recipes" % (len(favorite_by_users), numpy.mean(list(favorite_by_users.values()))))
        
        print("")
        print("== TOP RECIPES ==")
        
        for recipe_id, nb_recipes in sorted(favorite_recipes.items(), key=lambda x: x[1], reverse=True)[:10]:
            print("- %s : %i" % (recipe_by_id[recipe_id].name, nb_recipes))
        
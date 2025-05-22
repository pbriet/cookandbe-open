"""
Testing how meal time limit is constraining recipes
"""
from hippocrate.tests                       import HpUnidishApiTest
from common.mock_tools                      import empty_diet_decorator, fake_today_decorator,\
                                                   fake_redis_cache_decorator, fake_ratios_decorator
from hippocrate.models.database             import DishRecipe
from hippocrate_cpp.core                        import set_random_seed

from optalim.precache                       import cache_food_tags

import hippocrate.controls.constraint
import hippocrate.controls.filters
from mock import patch

class TestProteinsConstraint(HpUnidishApiTest):
    
    NB_MEALSLOTS            = 1 # 1 meal slot with 2 dishes
    NB_RECIPES              = 5
    WITH_INGREDIENTS        = False  # Added differently (see init_recipes)
    
    RECIPES_MEAT = {
        0: 0,
        1: 100,
        2: 50,
        3: 50,
        4: 0
     }
    
    RECIPES_FISH = {
        0: 0,
        1: 0,
        2: 100,
        3: 0,
        4: 50
     }
    def __init__(self, *args, **kargs):
        self.food_by_name = {}
        super().__init__(*args, **kargs)

    @fake_redis_cache_decorator
    def setUp(self):
        """
        Enables caching
        """
        super().setUp()

    def init_user(self):
        self.user.meat_level = 3 # Lot of meat
        self.user.fish_level = 1 # No fish please !
        self.user.save()

    def init_foods(self, **kargs):
        super().init_foods(**kargs)
        for i in range(2):
            self.init_food(i)
        cache_food_tags()

    def init_food(self, i):
        """
        Creates two foods : meat & fish, that are attached to food tags
        """
        if i == 0:
            food_name = "This meat"
            tag_names = ["Viande"] # Directly tagged
        elif i == 1:
            food_name = "This fish"
            tag_names = ["Poisson blanc", "Poisson"] # Tagged through hierarchy
            
        food = self.create_db_food(name = food_name)
        self.food_by_name[food_name] = food
        
        
        children = None
        tags = []
        for j, tag_name in enumerate(tag_names):
            foods = None
            if j == 0:
                # First tag is the one attached to the food
                foods = [food]
            tag = self.create_db_food_tag(tag_name, foods = foods,
                                          children=children)
            # This tag will be a child of the next one
            children = [tag]
            tags.append(tag)
        
        return food
    
    def init_recipes(self):
        super().init_recipes()
        for i, recipe in enumerate(self.recipes):
            meat, fish = self.RECIPES_MEAT[i], self.RECIPES_FISH[i]
            if meat > 0:
                self.create_db_ingredient(recipe, self.food_by_name["This meat"], meat)
            if fish > 0:
                self.create_db_ingredient(recipe, self.food_by_name["This fish"], fish)
    
    @fake_today_decorator()
    @empty_diet_decorator
    @fake_ratios_decorator(1)
    @patch.object(hippocrate.controls.constraint, "MEAT_LEVELS", {3: (130, -1, 0.2)})
    @patch.object(hippocrate.controls.constraint, "FISH_LEVELS", {1: (0, 30, 1.0)})
    def test_proteins_constraint(self):
        set_random_seed(42)
        
        # Planning calculation
        response = self._suggest_through_api()
        self.assertEqual(response.status_code, 200)
        
        # Retrieving the DishRecipes
        recipes = set()
        for dish_recipe in DishRecipe.objects.all():
            recipes.add(dish_recipe.recipe_id)
            
        EXPECTED_RECIPES = [self.recipes[1].id, # 100g meat  -  0g fish
                            self.recipes[3].id] # 50g meat   -  0g fish
        self.assertEqual(sorted(recipes), EXPECTED_RECIPES)
        
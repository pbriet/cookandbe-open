"""
Testing how dislike and pathologies are filtering recipes
"""
from common.test                            import TestAPIWithLogin
from mock                                   import patch
from optalim.config                          import Config
from hippocrate.controls.constraint         import ConstraintGenerator
from hippocrate.tests                       import HpUnidishApiTest
from profile_mgr.models                     import Profile
from collections                            import defaultdict

def fake_diet_constraints(self, *args):
    for c in []:
        yield c

class TestFoodTagApi(HpUnidishApiTest):
    def init_foods(self):
        super().init_foods()
        # Création des tags
        self.like       = self.create_db_food_tag(name = "like", foods = list(g for g in self.foods if g.id % 2 == 0))
        self.dislike    = self.create_db_food_tag(name = "dislike", foods = list(g for g in self.foods if g.id % 2 == 1))
        self.pathology  = self.create_db_food_tag(name = "pathology", foods = list(g for g in self.foods if g.id % 4 != 0))

    def _checkPlanningStructure(self, data):
        # Vérification de la structure du planning
        allDishRecipes = set()
        self.assertEqual(len(data["days"]), 7)
        for day in data["days"]:
            self.assertEqual(len(day["meal_slots"]), 1)
            for meal_type_id, meal in day["meal_slots"].items():
                self.assertEqual(len(meal["dishes"]), 2)
                for dish in meal["dishes"]:
                    self.assertEqual(len(dish["recipes"]), 1)
                    allDishRecipes.add(dish["recipes"][0]["name"])
        return allDishRecipes

    @patch.object(ConstraintGenerator, 'diet_constraints', fake_diet_constraints)
    def test_standard(self):
        # Génération du planning
        response = self._fill_through_api()
        
        # Contrôles
        self.assertEqual(response.status_code, 201)
        allDishRecipes = self._checkPlanningStructure(response.data)
        # Comme il y a 20 recettes pour 14 dishes et qu'on évite toujours les redondances, on devrait en trouver 14 différentes
        self.assertEqual(len(allDishRecipes), 14)

    @patch.object(ConstraintGenerator, 'diet_constraints', fake_diet_constraints)
    def test_with_dislikes(self):
        # Ajout du dislike au profil
        self.create_db_taste(self.dislike, self.profiles[0])
        # Génération du planning
        response = self._fill_through_api()
        # Contrôles
        self.assertEqual(response.status_code, 201)
        allDishRecipes = self._checkPlanningStructure(response.data)
        # Aucune recette ne doit avoir d'ingrédient avec tag dislike
        for recipe in self.recipes:
            if recipe.name in allDishRecipes:
                for ingredient in recipe.ingredients.all():
                    self.assertTrue(self.dislike not in ingredient.food.tags.all())
        # Comme il ne reste que 10 recettes (après filtrage sur les dislike) et qu'on évite toujours les redondances, les 10 devraient être utilisées
        self.assertTrue(len(allDishRecipes), 10)

    @patch.object(ConstraintGenerator, 'diet_constraints', fake_diet_constraints)
    def test_with_pathologies(self):
        # Ajout de la pathologie au profil
        self.create_db_restricted_food(self.pathology, self.profiles[0])
        # Génération du planning
        response = self._fill_through_api()
        # Contrôles
        self.assertEqual(response.status_code, 201)
        allDishRecipes = self._checkPlanningStructure(response.data)
        # Aucune recette ne doit avoir d'ingrédient avec tag pathology
        for recipe in self.recipes:
            if recipe.name in allDishRecipes:
                for ingredient in recipe.ingredients.all():
                    self.assertTrue(self.pathology not in ingredient.food.tags.all())
        # Comme il ne reste que 5 recettes (après filtrage sur les pathologies) et qu'on évite toujours les redondances, les 5 devraient être utilisées
        self.assertTrue(len(allDishRecipes), 5)

class TestMultiProfileFoodTagApi(HpUnidishApiTest):
    NB_FOODS            = 6
    NB_RECIPES          = 6
    NB_MEALSLOTS        = 6
    NB_DISHES_PER_MEAL  = 1
    NB_PROFILES         = 0
    NB_SLOTS_PER_DAY    = 1

    JABBA_EATING_DAYS   = (0, 2, 4, 5)
    C3PO_EATING_DAYS    = (1, 2, 3, 5)

    JABBA_ONLY_FOODS    = (0, 1, 2)
    C3PO_ONLY_FOODS     = (2, 4, 5)

    def init_main_profile(self):
        luke = self.create_db_profile(nickname='Luke')
        self.luke = self.create_db_eater(luke)
        self.eaters.append(self.luke)
        self.profiles.append(luke)
        self.assertEqual(self.user.main_profile, luke)

    def init_foods(self):
        super().init_foods()
        self.init_main_profile()
        self.organic        = self.create_db_food_tag(name = "organic", foods = list(self.foods[i] for i in self.JABBA_ONLY_FOODS))
        self.electronical   = self.create_db_food_tag(name = "electronical", foods = list(self.foods[i] for i in self.C3PO_ONLY_FOODS))
        # Creating 2 profiles and corresponding eaters
        p = self.create_db_profile(nickname='jabba the hutt')
        self.profiles.append(p)
        self.jabba = self.create_db_eater(p)
        self.eaters.append(self.jabba)
        p = self.create_db_profile(nickname='C-3PO')
        self.profiles.append(p)
        self.c3po = self.create_db_eater(p)
        self.eaters.append(self.c3po)
        self.assertEqual(Profile.objects.filter(creator=self.user).count(), 3)
        # Adding tastes
        self.create_db_taste(profile = self.jabba.profile, foodTag = self.electronical, dislike = True)
        self.create_db_taste(profile = self.c3po.profile,  foodTag = self.organic, dislike = True)

    def init_meal_slot(self, meal_slot_number, planning = None, week_day = 0, speed = 2, eaters = None):
        # The idea is to check that darwin allows forbidden food tags when eaters are away
        eaters = [self.luke]
        if meal_slot_number in self.JABBA_EATING_DAYS:
            eaters.append(self.jabba)
        if meal_slot_number in self.C3PO_EATING_DAYS:
            eaters.append(self.c3po)
        return super().init_meal_slot(meal_slot_number, planning, week_day, speed, eaters)

    @patch.object(ConstraintGenerator, 'diet_constraints', fake_diet_constraints)
    def test_multi_profile_taste(self):
        # Computing planning
        response = self._fill_through_api()
        self.assertEqual(response.status_code, 201)
        # Checking recipes
        for i_day, day in enumerate(response.data["days"]):
            for meal_slot_id, meal_slot_data in day["meal_slots"].items():
                recipeName = meal_slot_data["dishes"][0]["recipes"][0]["name"]
                print("meal_slot_data", meal_slot_data)
                print("i_day", i_day)
                if i_day in self.JABBA_EATING_DAYS:
                    print("jabba eats", recipeName, int(recipeName[-1]) not in self.C3PO_ONLY_FOODS)
                    self.assertTrue(int(recipeName[-1]) not in self.C3PO_ONLY_FOODS)
                if i_day in self.C3PO_EATING_DAYS:
                    print("C3PO eats", recipeName, int(recipeName[-1]) not in self.JABBA_ONLY_FOODS)
                    self.assertTrue(int(recipeName[-1]) not in self.JABBA_ONLY_FOODS)

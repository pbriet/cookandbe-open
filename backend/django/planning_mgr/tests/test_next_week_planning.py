from common.test            import TestAPIWithLogin
from common.date            import tz_aware
from planning_mgr.models    import Day, MetaPlanning, MealSlot, Dish, MealSlotEater, DishRecipe

from recipe_mgr.models      import DishType, Recipe, Ingredient
from eater_mgr.models       import Eater
from mock                   import patch
import planning_mgr.views
import datetime

class TestAddWeekAPI(TestAPIWithLogin):

    def test_nextweek_existing(self):
        self.user.meta_planning = self.create_db_meta_planning()
        self.user.save()
        planning = self.create_db_planning(start_date=tz_aware(datetime.datetime(2014, 2, 3)))
        days = planning.sorted_days

        for day in days:
            response = self.client.get('/api/user/%i/day/%s' % (self.user.id, day.date))
            self.assertEqual(response.status_code, 200)
            self.assertEqual(response.data["date"], str(day.date))

class TestInitNextWeekWithoutMeta(TestAPIWithLogin):
    def test_init_next_week_without_meta(self):
        response = self.client.post('/api/user/%i/add_days/2010-01-01' % self.user.id)
        self.assertEqual(response.status_code, 400)
        self.assertEqual(response.data['error'], 'user has no metaplanning')

class TestInitNextWeekWithMeta(TestAPIWithLogin):
    def setUp(self):
        TestAPIWithLogin.setUp(self)
        self.init_db_profile_eater()
        self.init_default_meal_type_settings()
        self.nb_default_test_recipes = Recipe.objects.count()
        self.nb_default_test_ingredients = Ingredient.objects.count()

        self.dish_type = self.create_db_dishtype()

        self.meta = self.create_db_meta_planning(with_n_days=1)
        self.day  = self.meta.sorted_days[0]
        
        self.user.meta_planning = self.meta
        self.user.save()
        self.meal_slot1 = self.create_db_mealslot(self.day)
        self.meal_slot2 = self.create_db_mealslot(self.day)
        self.meal_slot3 = self.create_db_mealslot(self.day, suggest = False)
        
        self.dish1 = self.create_db_dish(self.meal_slot1, self.dish_type)
        self.dish2_1 = self.create_db_dish(self.meal_slot2, self.dish_type)
        self.dish2_2 = self.create_db_dish(self.meal_slot2, self.dish_type)
        
        # Some custom dish/recipe
        self.dish3 = self.create_db_dish(self.meal_slot3, DishType.get_dt(DishType.DT_CUSTOM))
        self.custom_recipe = self.create_db_recipe(internal = True)
        self.create_db_ingredient(self.custom_recipe, self.create_db_food(), 42)
        self.create_db_dishrecipe(self.dish3, self.custom_recipe)
    
    def _check_db_object(self, nb_weeks):
        self.assertEqual(Day.objects.count(), 7 * (nb_weeks - 1) + 1)
        self.assertEqual(MealSlot.objects.count(), 3 * nb_weeks)
        self.assertEqual(Dish.objects.count(), 4 * nb_weeks)
        self.assertEqual(MealSlotEater.objects.count(), 3 * nb_weeks)
        self.assertEqual(Eater.objects.count(), 1)
        self.assertEqual(Recipe.objects.filter(internal = True).count(), 1 * nb_weeks)
        self.assertEqual(Recipe.objects.filter(internal = False).count(), self.nb_default_test_recipes)
        self.assertEqual(Ingredient.objects.count(), nb_weeks + self.nb_default_test_ingredients)
        self.assertEqual(DishRecipe.objects.count(), nb_weeks)

    def test_add_week(self):
        self._check_db_object(1)
        response = self.client.post('/api/user/%i/add_days/2010-01-01' % self.user.id)
        self.assertEqual(response.status_code, 201)
        self._check_db_object(2)

        last_day = Day.objects.order_by('-date')[0]

        for meal_slot in last_day.meal_slots.all():
            self.assertTrue(meal_slot.id not in [self.meal_slot1.id, self.meal_slot2.id, self.meal_slot3.id])
            for dish in meal_slot.dishes.all():
                self.assertTrue(dish.id not in [self.dish1.id, self.dish2_1.id, self.dish2_2.id, self.meal_slot3.id])

class TestGeneratePlanningFromMetaWithExternals(TestAPIWithLogin):
    def init_default_meal_place_settings(self, *args):
        # Initializing MealPlace table
        place_names = ("home", "donoteat", "away")
        self.places = dict((key, self.create_db_mealplace(key)) for key in place_names)

    def setUp(self):
        super().setUp()
        self.init_default_meal_type_settings()
        # Deux personnes
        self.init_db_profile_eater()
        self.init_db_profile_eater()
        # Création de recettes
        self.dt_home = DishType.get_dt(DishType.DT_MAIN_COURSE)
        self.dt_external = DishType.get_dt(DishType.DT_EXTERNAL)
        self.recipes = (
            self.create_db_recipe("Repas à l'extérieur", dish_types = [self.dt_external]),
            self.create_db_recipe("Repas cuisiné", dish_types = [self.dt_home])
        )
        # Création du metaplanning
        self.meta = self.create_db_meta_planning(with_n_days=1)
        self.day  = self.meta.sorted_days[0]
        
        # Ajout de meal_slots home/external
        self.meal_slots = (
            self.create_db_mealslot(self.day, meal_place = self.places["home"]),
            self.create_db_mealslot(self.day, meal_place = self.places["donoteat"]),
            self.create_db_mealslot(self.day, meal_place = self.places["away"])
        )
        # Ajout des DishType tous en "home" qui seront convertis en "external" à la génération du planning
        self.dishes = (
            self.create_db_dish(self.meal_slots[0], self.dt_home),
            self.create_db_dish(self.meal_slots[0], self.dt_home),
            self.create_db_dish(self.meal_slots[1], self.dt_home),
            self.create_db_dish(self.meal_slots[1], self.dt_home),
            self.create_db_dish(self.meal_slots[2], self.dt_home),
            self.create_db_dish(self.meal_slots[2], self.dt_home)
        )

    def test_add_week(self):
        self.assertEqual(Day.objects.count(), 1)
        self.assertEqual(MealSlot.objects.count(), 3)
        self.assertEqual(Dish.objects.count(), 6)
        self.assertEqual(MealSlotEater.objects.count(), 6)
        self.assertEqual(Eater.objects.count(), 2)
        self.assertEqual(DishRecipe.objects.count(), 0)
        # Génération du planning
        response = self.client.post('/api/user/%i/add_days/2010-01-01' % self.user.id)
        self.assertEqual(response.status_code, 201)
        # Contrôle du planning
        self.assertEqual(Day.objects.count(), 8)
        # MealSlot : 3 metaplanning + 1 par repas à la maison ou à l'extérieur
        self.assertEqual(MealSlot.objects.count(), 5)
        self.assertEqual(MealSlot.objects.filter(meal_place__key = "donoteat").count(), 1)
        self.assertEqual(MealSlot.objects.filter(meal_place__key = "home").count(), 2)
        self.assertEqual(MealSlot.objects.filter(meal_place__key = "away").count(), 2)
        # Dish : 6 metaplanning + 2 par repas à la maison, 2 par repas à l'extérieur, aucun en "donoteat"
        self.assertEqual(Dish.objects.count(), 10)
        self.assertEqual(Dish.objects.filter(dish_type = self.dt_home).count(), 10)
        # There used to be dishes with external dish_type. Not anymore
        self.assertEqual(Dish.objects.filter(dish_type = self.dt_external).count(), 0)
        # Eater : 6 metaplanning + 2 par repas à la maison, 1 par repas à l'extérieur, aucun en "donoteat"
        self.assertEqual(MealSlotEater.objects.count(), 9)
        self.assertEqual(MealSlotEater.objects.filter(eater = self.eaters[0]).count(), 5)
        self.assertEqual(MealSlotEater.objects.filter(eater = self.eaters[1]).count(), 4)
        self.assertEqual(Eater.objects.count(), 2)
        # No forced recipes
        self.assertEqual(DishRecipe.objects.count(), 0)

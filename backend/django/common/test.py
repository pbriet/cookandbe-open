"""
Some useful classes / functions to help testing
"""

from collections                    import defaultdict
from django.core.exceptions         import ObjectDoesNotExist
from smart_testing.testcase         import BaseTestCase
from django.utils                   import timezone
from functools                      import update_wrapper
from mock                           import patch
from unittest                       import skip
from rest_framework.test            import APIClient
from django.utils.timezone          import make_aware

from blogs.models                   import Blog

from common.date                    import tz_aware, today, add_months, add_days
from common.model                   import AutoUrlKeyModel

from diet_mgr.models                import Diet, UserDietParameter
import diet_mgr.handlers.anc

from eater_mgr.models               import Eater

from hippocrate.models.recipestorage  import MainRecipeStorage
from hippocrate.models.problem      import Problem

from location_mgr.models            import Location

from notify_mgr.models              import Information

from optalim.config                 import Config
import optalim.settings

from nutrient.helpers               import RecipeNutrientCalculator
from nutrient.models                import Nutrient, FoodNutrient, CookingMethodEffect, NutrientPack

from paybox.models                  import Subscription, Transaction, UserSpecialOffer, GlobalSpecialOffer

from planning_mgr.models            import MealSlot, MealSlotEater, Dish, DishType, Day, Planning
from planning_mgr.models            import MetaPlanning, DishRecipe, MealType, MealDishOption, MealPlace

from profile_mgr.models             import Profile, Taste, RestrictedFood, RecipeDislike, ProfileMetric

from recipe_mgr.models              import Recipe, Food, Ingredient, RawState, CookingMethod, FoodTag, FoodTagSet
from recipe_mgr.models              import FoodType, FoodConversion, UstensilCategory, Ustensil
from recipe_mgr.models              import RecipeDishType, DishTypeAggregation, RecipeTag, RecipeInstruction
from recipe_mgr.models              import FoodSeasonality, RecipeRating, CookbookRecipe

from shopping_mgr.models            import ShoppingCategory, ShoppingList, ShoppingItem

from discussion.models              import Message, Discussion, Publication

from user_mgr.models                import User, ProUser
from user_mgr.models                import ConfigStage, ConfigStageCompletion, Role, BaseUserRole

from memory.controls                import MemoryManager

import datetime
import os
import re

class BaseOptalimTest(BaseTestCase):
    # Test settings
    CREATE_DEFAULT_USER = True
    PERMISSIONS         = tuple() # E.g: Put ("admin", ) to give an admin role. User "@add_permissions" to set it for a specific method
    INIT_CLIENT_API     = True
    LOGIN_ON_STARTUP    = False
    INITIALIZE_RECIPE_INDEXER = False # Allows to use MainRecipeStorage normally
    # Default credentials
    LOGIN       = 'test@test.fr'
    PASSWORD    = 'try_me'
    MAIL        = property(lambda x: x.LOGIN)
    USERNAME    = 'kaloo'
    # Shortcuts
    now         = property(lambda x: timezone.now())
    today       = property(lambda x: x.now.date())

    def __init__(self, *args, **kargs):
        self.profiles   = []
        self.eaters     = []
        self.ustensil_categories = None
        self.places     = None
        self.has_profile_metrics = False # Do we have created profile metrics ? (required for profile creation)
        # During testing, all passwords are kept unciphered
        self._passwords = dict()
        self.access_token = None
        super().__init__(*args, **kargs)

    def setUp(self):
        super().setUp()
        DishType.reset()
        Nutrient.reset()
        RawState.clear_cached()
        self.init_default_roles()
        self.init_default_diet()
        self.france = Location.objects.create(name="France")
        self.food_type = None
        self.default_shopping_category = self.create_db_shopping_category(name="shopping_category_x")
        MemoryManager.initialize()
        # Apply settings
        if self.CREATE_DEFAULT_USER:
            self._create_default_user()
        if self.INIT_CLIENT_API:
            self.client = APIClient()
        else:
            self.client = None
        if self.LOGIN_ON_STARTUP:
            self.api_login()

        if self.INITIALIZE_RECIPE_INDEXER:
            # Allows to use MainRecipeStorage normally.
            # WARNING: you must call that after creating the nutrients.
            MainRecipeStorage.init_indexer()

    def api_logout(self):
        self.access_token = None
        # Stop including any credentials
        self.client.credentials()

    def api_login(self, login=None, password=None):
        self.access_token = None
        if login is None:
            login = self.LOGIN
        if password is None:
            password = self.PASSWORD

        response = self.client.post('/api/token/', {'email': login, 'password': password})
        self.set_jwt_access_token(response.data['access'])
        return True

    def set_jwt_access_token(self, value):
        """
        Set the access token to use in HTTP transactions
        """
        self.access_token = value
        self.client.credentials(HTTP_AUTHORIZATION='Bearer ' + value)

    def change_user(self, user):
        if user is not None:
            login = user.email
            password = self._passwords[user.email]
        # Unlogging
        self.api_logout()
        if user is None:
            # Anonymous
            return
        self.assertTrue(self.api_login(login = login, password = password), "Fail to login with username '%s' and password '%s'" % (login, password))

    def reload_user(self):
        self.user = User.objects.get(pk=self.user.id)

    def init_default_nutrients(self):
        return self.create_db_nutrient("energiekilocalories")

    def init_default_ingredient_settings(self):
        """
        Creates default RawState and CookingMethod
        """
        if hasattr(self, 'raw') and hasattr(self, 'not_cooked'):
            return
        self.raw        = RawState.objects.create(name = "frais")
        self.not_cooked = self.create_db_cooking_method(name = "cru")

    def init_default_diet(self):
        self.diet       = self.create_db_diet("balanced", title="Classique", description="(description")

    def init_default_meal_place_settings(self):
        # Initializing MealPlace table
        place_names = ("home", "donoteat", "lunchpack", "away")
        self.places = dict((key, self.create_db_mealplace(key)) for key in place_names)

    def init_default_meal_type_settings(self):
        # Clearing tables
        MealDishOption.objects.all().delete()
        DishType.objects.all().delete()
        MealType.objects.all().delete()

        # Initializing DishType table
        dishTypes = dict()
        dishInfos = [
            # Ref   Name                          Calories
            (1,     DishType.DT_BREAKFAST_BASE,   337),
            (2,     DishType.DT_STARTER,          223),
            (3,     DishType.DT_MAIN_COURSE,      352),
            (4,     DishType.DT_FULL_COURSE,      505),
            (5,     DishType.DT_SIDE,             224),
            (6,     DishType.DT_CHEESE,           102),
            (7,     DishType.DT_DESSERT,          150),
            (8,     DishType.DT_SNACK,            145),
            (9,     DishType.DT_SNACK_SALTED,     148),
            (10,    DishType.DT_SNACK_SWEET,      142),
            (11,    DishType.DT_BEVERAGE,         52),
            (12,    DishType.DT_BEVERAGE_HOT,     20),
            (13,    DishType.DT_BEVERAGE_COLD,    85),
            (14,    DishType.DT_MILKY,            125),
            (15,    DishType.DT_FRUIT,            71),
            (16,    DishType.DT_BREAD,            192),
            (17,    DishType.DT_EXTERNAL,         None),
            (18,    DishType.DT_CUSTOM,           None),
        ]
        for ref, name, calories in dishInfos:
            dishTypes[ref] = self.create_db_dishtype(name = name, standard_calories=calories)

        # Initializing MealType table
        self.init_default_meal_place_settings()
        mealTypes = dict()
        mealInfos = [
            # Ref   Key             Name                Nickname        Time                        Place       default  forced
            (1,     "breakfast",    "Petit déjeuner",   "Petit déj",    datetime.time( 8, 30, 0),   "home",     False,   False),
            (2,     'morning_snack',"Collation",        "Collation",    datetime.time(10, 30, 0),   "donoteat", False,   False),
            (3,     'lunch',        "Déjeuner",         "Déjeuner",     datetime.time(12, 30, 0),   "home",     True,    True),
            (4,     'snack',        "Goûter",           "Goûter",       datetime.time(16, 30, 0),   "donoteat", False,   False),
            (5,     'dinner',       "Dîner",            "Dîner",        datetime.time(19, 30, 0),   "home",     True,    True)
        ]
        for ref, key, name, nickname, time, default_place, default_suggest, force_suggest in mealInfos:
            mealTypes[ref] = self.create_db_mealtype(name = name, key = key, nickname = nickname, time = time,
                                                     default_place = self.places[default_place],
                                                     default_suggest = default_suggest, force_suggest = force_suggest)

        # Initializing aggregated dish types
        DishTypeAggregation.objects.create(master_dish_type = dishTypes[4], sub_dish_type = dishTypes[3])
        DishTypeAggregation.objects.create(master_dish_type = dishTypes[4], sub_dish_type = dishTypes[5])

        # Create default recipes
        self.init_default_ingredient_settings()
        default_recipes = defaultdict(lambda: None)
        for dish_type_id in (1, 9, 11, 12, 13, 14):
            recipe = self.create_db_recipe("Default %s" % dishTypes[dish_type_id].name, dish_types=[dishTypes[dish_type_id]])
            self.create_db_ingredient(recipe, self.create_db_food("Default food for %s" % dishTypes[dish_type_id].name), 42)
            default_recipes[dish_type_id] = recipe



        # Initializing MealDishOption table
        mealDishOptions = dict()
        mealDishInfos = [
            # Ref   MealType    DishType        Minspeedcheck   Minbudgetcheck    SatietyPoints
            # Petit-Déjeuner
            (1,     1,          1,              1,              1,                20), # Base (céréales...)
            (2,     1,          9,              None,           None,             15), # Fruit
            (3,     1,          12,             1,              1,                10), # Boisson chaude
            (4,     1,          11,             None,           None,             10), # Boisson froide
            # Collation
            (5,     2,          13,             None,           None,             15), # Snack sucré
            (6,     2,          14,             None,           None,             15), # Snack salé
            (7,     2,          9,              1,              1,                10), # Fruit
            (8,     2,          11,             None,           None,             10), # Boisson froide
            (9,     2,          12,             None,           None,             10), # Boisson chaude
            # Déjeuner
            (10,    3,          2,              3,              2,                20), # Entree
            (11,    3,          4,              1,              1,                60), # Plat complet
            (13,    3,          15,             1,              1,                10), # Pain
            (14,    3,          6,              2,              2,                15), # Fromage
            (15,    3,          7,              1,              1,                20), # Dessert
            (16,    3,          12,             None,           None,             0), # Boisson chaude
            (17,    3,          11,             None,           None,             0), # Boisson froide
            # Goûter
            (18,    4,          13,             1,              1,                20), # Snack sucré
            (19,    4,          14,             None,           None,             20), # Snack salé
            (20,    4,          9,              3,              1,                15), # Fruit
            (21,    4,          11,             None,           None,             10), # Boisson froide
            (22,    4,          12,             None,           None,             10), # Boisson chaude
            # Dîner
            (23,    5,          2,              2,              2,                20), # Entree
            (24,    5,          4,              1,              1,                60), # Plat complet
            (25,    5,          15,             1,              1,                10), # Pain
            (26,    5,          6,              1,              1,                15), # Fromage
            (27,    5,          7,              1,              1,                20), # Dessert
            (28,    5,          12,             None,           None,             0), # Boisson chaude
            (29,    5,          11,             None,           None,             0), # Boisson froide
        ]

        for ref, meal_ref, dish_ref, min_speed_check, min_budget_check, points in mealDishInfos:
            mealDishOptions[ref] = self.create_db_mealdishoption(mealTypes[meal_ref], dishTypes[dish_ref],
                                                                 min_budget_check = min_budget_check,
                                                                 min_speed_check = min_speed_check,
                                                                 default_recipe = default_recipes[dish_ref])
            if default_recipes[dish_ref]:
                # Adding default static option
                mealTypes[meal_ref].static_recipe_options.add(default_recipes[dish_ref])
        # Initializing MealPlace
        self.get_default_mealplace()

    def init_db_profile_eater(self):
        """
        Create a profile and a eater for self.user
        """
        self.profiles.append(self.create_db_profile())
        self.eaters.append(self.create_db_eater(self.profiles[-1]))

    def init_default_roles(self):
        self.role_admin     = self.create_db_role("admin",      id=Role.R_ADMIN)
        self.role_author    = self.create_db_role("author",     id=Role.R_AUTHOR)
        self.role_moderator = self.create_db_role("moderator",  id=Role.R_MODERATOR)
        self.role_reviewer  = self.create_db_role("reviewer",   id=Role.R_REVIEWER)
        self.role_operator  = self.create_db_role("operator",   id=Role.R_OPERATOR)
        self.role_developer = self.create_db_role("developer",  id=Role.R_DEVELOPER)
        self.role_dietician = self.create_db_role("dietician",  id=Role.R_DIETICIAN)

    def create_db_role(self, name = None, id = None):
        if name is None: name = "Role %i" % Role.objects.all().count() + 1
        role, created = Role.objects.get_or_create(id=id, defaults={"name": name})
        return role

    def create_db_dishtype(self, name=None, standard_calories=300, monotonous=False):
        if name is None:
            name="breakfast"
        return DishType.objects.create(name=name, standard_calories=standard_calories, monotonous=monotonous)

    def create_db_diet(self, key=None, title=None, description=None, default_display=True,
                             min_subscription_level=0, has_diagnostic=False, enabled=True,
                             url_key=None, free_trial_days=10, email_title=None):
        if key is None:
            key = "my_diet"
        if title is None:
            title = "Regime '%s'" % key
        if email_title is None:
            email_title = ""
        if url_key is None:
            url_key = AutoUrlKeyModel._build_base_key(title)
        if description is None:
            description = "fake description"
        res = Diet.objects.create(key=key, title=title, description=description, default_display=default_display,
                                  url_key=url_key, free_trial_days=free_trial_days, email_title=email_title,
                                  min_subscription_level=min_subscription_level, has_diagnostic=has_diagnostic, enabled=enabled)
        return res

    def assign_diet_user(self, user, diet, **parameters):
        """
        Assign a diet to a user, with settings
        """
        self.user.diet = diet
        self.user.diet_changed_at = timezone.now()
        self.user.save()
        UserDietParameter.objects.filter(user=user).delete()
        for key, value in parameters.items():
            if type(value) is str:
                float_value, string_value = None, value
            else:
                float_value, string_value = value, None
            UserDietParameter.objects.create(user=user, name=key, float_value=float_value, string_value=string_value)

    def create_db_dishtype_aggregated(self):
        """
        Returns 3 dishtypes : the first one is the aggregation of the 2 others
        """
        dish_type1 = self.create_db_dishtype("main")
        dish_type2 = self.create_db_dishtype("side")
        dish_type_agg = self.create_db_dishtype("full meal")
        DishTypeAggregation.objects.create(master_dish_type = dish_type_agg, sub_dish_type = dish_type1)
        DishTypeAggregation.objects.create(master_dish_type = dish_type_agg, sub_dish_type = dish_type2)
        return dish_type_agg, dish_type1, dish_type2

    def create_db_cookbookrecipe(self, recipe, user=None):
        if user is None: user = self.user
        return CookbookRecipe.objects.create(recipe=recipe, user=user)

    def create_db_ustensil_category(self, name = None):
        if name is None: name = "Ustensil category"
        return UstensilCategory.objects.create(name = name)

    def get_default_ustensil_category(self):
        if self.ustensil_categories is None:
            self.ustensil_categories = dict((key, self.create_db_ustensil_category(key)) for key in ("classical", "advanced"))
        return self.ustensil_categories["classical"]

    def create_db_ustensil(self, name = None, category = None, default_check = False):
        if name is None: name = "Ustensil"
        if category is None: category = self.get_default_ustensil_category()
        return Ustensil.objects.create(name = name, category = category, default_check = default_check)

    def create_db_cooking_method(self, name = "test cooking method"):
        return CookingMethod.objects.create(name = name)

    def create_db_cooking_method_effect(self, food_type, cooking_method, weight_ratio):
        return CookingMethodEffect.objects.create(food_type=food_type,
                                                  cooking_method=cooking_method,
                                                  weight_ratio=weight_ratio)

    def create_db_raw_state(self, name = "test cooking method"):
        return RawState.objects.create(name = name)

    def create_db_ingredient(self, recipe, food, grams=100, raw_state=None, cooking_method=None,
                                   default_conversion=None):
        """
        Creates a new ingredient in db, with default raw_state, cooking_method if not provided
        """
        if raw_state is None:
            assert hasattr(self, "raw"), "please call self.init_default_ingredient_settings() before create_db_ingredient"
            raw_state = self.raw
        if cooking_method is None:
            assert hasattr(self, "not_cooked"), "please call self.init_default_ingredient_settings() before create_db_ingredient"
            cooking_method = self.not_cooked
        if default_conversion is None:
            if food.conversions.count() > 0:
                default_conversion = list(food.conversions.all())[0]
            else:
                default_conversion = self.create_db_food_conversion(food=food, unit="g", value=1)

        return Ingredient.objects.create(recipe=recipe, food=food, grams=grams, raw_state=raw_state,
                          cooking_method=cooking_method, default_conversion=default_conversion)

    def create_db_instruction(self, recipe, text = None):
        if text is None:    text = "Test instruction"
        return RecipeInstruction.objects.create(recipe = recipe, text = text)

    def create_db_recipe(self, name="my recipe", author=None, price=1, id=None,
                              prep_minutes=10, cook_minutes=0, rest_minutes=0, difficulty=1, nb_people=2,
                              dish_types=None, status=3, ustensils=None, tags=None, internal=False,
                              photo=None, blog=None):
        if author is None:
            author = self.user
        recipe = Recipe.objects.create(name=name, author=author, price=price,
                                     prep_minutes=prep_minutes, cook_minutes=cook_minutes, rest_minutes=rest_minutes,
                                     difficulty=difficulty, nb_people=nb_people, status=status, id=id, internal=internal,
                                     photo=photo)
        if dish_types is not None:
            for dish_type in dish_types:
                RecipeDishType.objects.create(recipe=recipe, dish_type=dish_type)
        if ustensils is not None:
            for ustensil in ustensils:
                recipe.ustensils.add(ustensil)
        if tags is not None:
            recipe.tags.add(*tags)
        return recipe

    def create_db_foodtype(self, name="this kind of food", fresh_expiry=None, usually_stored=False):
        return FoodType.objects.create(name=name, fresh_expiry=fresh_expiry, usually_stored=usually_stored)

    def create_db_food(self, name="test food", full_name=None, enabled=True, food_type=None, shopping_category=None,
                       with_conversion=False, default_raw_state=None, default_cooking_method=None, fresh_expiry=None):
        if full_name is None:
            full_name = name
        if food_type is None:
            if not self.food_type:
                self.food_type = self.create_db_foodtype()
            food_type = self.food_type
        if shopping_category is None:
            shopping_category = self.default_shopping_category
        food = Food.objects.create(name=name, full_name=name, enabled=enabled,
                                   type=food_type, shopping_category=shopping_category, fresh_expiry=fresh_expiry,
                                   default_raw_state=default_raw_state, default_cooking_method=default_cooking_method)
        if with_conversion:
            self.create_db_food_conversion(food = food)
        MemoryManager.initialize()
        return food

    def create_db_food_seasonality(self, food_id, start_month, end_month):
        return FoodSeasonality.objects.create(food_id=food_id, start_month=start_month, end_month=end_month)

    def create_db_shopping_category(self, name, list_order=None):
        if list_order is None:
            list_order = ShoppingCategory.objects.count()
        res = ShoppingCategory.objects.create(name=name, list_order=list_order)
        return res

    def create_db_shopping_list(self, start_date=None, end_date=None, user=None):
        if start_date is None:
            start_date = "2014-01-26"
        if end_date is None:
            end_date = "2014-01-29"
        if user is None:
            user = self.user
        if type(start_date) is str:
            start_date = tz_aware(datetime.datetime.strptime(start_date, "%Y-%m-%d")).date()
        if type(end_date) is str:
            end_date = tz_aware(datetime.datetime.strptime(end_date, "%Y-%m-%d")).date()
        res = ShoppingList.objects.create(user=user, start_date=start_date, end_date=end_date)
        for day in Day.objects.filter(user=user, date__gte=start_date, date__lte=end_date):
            day.shopping_list = res
            day.save()
        return res

    def create_db_shopping_item(self, shopping_list, food=None, raw_state=None, grams=None, forced_name=None,
                                ingredient=None, got_it=False, forced_quantity=None, ratio=1, custom=False):
        if ingredient is None:
            assert custom or (food is not None and raw_state is not None and grams is not None), "For a non custom Food, you must give food+raw_state+grams OR an ingredient"
        else:
            if grams is None:
                grams = ingredient.grams_without_loss * ratio
            food = ingredient.food
            raw_state = ingredient.raw_state
        if custom:
            if forced_name is None:     forced_name = food.name or "Custom"
            if forced_quantity is None: forced_quantity = grams and str(grams)
        return ShoppingItem.objects.create(shopping_list=shopping_list,
                                           food=food,
                                           raw_state=raw_state,
                                           grams=grams,
                                           got_it=got_it,
                                           forced_quantity=forced_quantity,
                                           forced_name=forced_name)

    def create_db_food_tag(self, name="tagged food", foods = None, id=None, children=None, can_be_disliked=True):
        res = FoodTag.objects.create(name=name, id=id, can_be_disliked=can_be_disliked)
        if foods is not None:
            for f in foods:
                FoodTagSet.objects.create(tag = res, food = f)
        if children is not None:
            for c in children:
                res.children.add(c)
        return res

    def db_assign_food_to_foodtag(self, food, food_tag):
        FoodTagSet.objects.create(food=food, tag=food_tag)

    def create_db_recipe_tag(self, name="awesome tag", parent=None, id=None):
        return RecipeTag.objects.create(name=name, parent=parent, id=id)

    def create_db_food_conversion(self, food, unit="g", value=50, loss_coeff=0, plural=None, shopping_compatible=True):
        if plural is None:
            plural = unit
        return FoodConversion.objects.create(unit=unit, food=food, value=value, loss_coeff=loss_coeff,
                                             unit_plural=plural, shopping_compatible=shopping_compatible)

    def create_db_nutrient(self, name="Midichlorien", short_name=None, unit="mg", id=None, key=None):
        if short_name is None:
            short_name = name # dpm
        if key is None:
            key = re.compile('\W+').sub('', short_name.lower()).strip()
        return Nutrient.objects.create(name=name, short_name=short_name, unit=unit, id=id, key=key)

    def create_db_nutrient_pack(self):
        return NutrientPack.objects.create(key="toto", title="titi", description="tata", order=1)

    def create_db_foodnutrient(self, food, nutrient, amount_per_gram, raw_state=None, cooking_method=None):
        if raw_state is None:
            assert hasattr(self, "raw"), "please call self.init_default_ingredient_settings() before create_db_foodnutrient"
            raw_state = self.raw
        if cooking_method is None:
            assert hasattr(self, "not_cooked"), "please call self.init_default_ingredient_settings() before create_db_foodnutrient"
            cooking_method = self.not_cooked

        return FoodNutrient.objects.create(food=food, nutrient=nutrient, amount_per_gram=amount_per_gram,
                                    raw_state=raw_state, cooking_method=cooking_method)

    def _create_db_user(self, email = None, name = None, password = None, super_user = False, roles = None,
                       date_joined=None, cls=User):
        if email is None:       email = 'user_%i@test.fr' % (cls.objects.count() + 1)
        if name is None:        name  = 'user %i' % (cls.objects.count() + 1)
        if password is None:    password = self.PASSWORD
        if super_user:
            fcn = cls.objects.create_superuser
        else:
            fcn = cls.objects.create_user
        user = fcn(email, first_name = name, password = password)
        if date_joined is not None:
            if type(date_joined) is datetime.date:
                date_joined = datetime.datetime.combine(date_joined, datetime.datetime.min.time())
            user.date_joined = tz_aware(date_joined)
            user.save()
        assert email not in self._passwords, "User email collision"
        self._passwords[email] = password
        if roles is not None:
            for role_name in roles:
                self.create_db_user_role(user, role_name, creator = user)
        return user

    def create_db_pro_user(self, *args, **kargs):
        kargs['cls'] = ProUser
        return self._create_db_user(*args, **kargs)

    def create_db_user_role(self, user, role_name, creator = None):
        if creator is None:
            creator = self.user
        return BaseUserRole.objects.create(user = user, role = Role.objects.get(name = role_name), created_by = creator)

    def init_profile_metrics(self):

        METRICS = [('height', 'Hauteur', 'Taille en cm'),
                   ('weight', 'Poids', 'Poids en kg'),
                   ('metabolism', 'Métabolisme', 'Capacité d\'absorption des aliments')]
        for (key, name, description) in METRICS:
            ProfileMetric.objects.create(key=key, name=name, description=description)
        self.has_profile_metrics = True

    def create_db_profile(self, nickname="bob", creation_date=None, modification_date=None,
                                weight=56, height=185, birth_date=datetime.datetime(1985, 1, 13), sex="male",
                                work_score=None, moving_score=None, sport_score=None, creator=None,
                                auto_set_main_profile=True, metabolism=1.0, forced_base_calories=None):
        if creation_date is None:
            creation_date = timezone.now()
        if modification_date is None:
            modification_date = timezone.now()
        if creator is None and hasattr(self, 'user'):
            creator = self.user
        #The following line adds timezone info in the birth_date to avoid a warning from the ORM
        birth_date = tz_aware(birth_date)

        if not self.has_profile_metrics:
            # Profile metrics are required for the profile creation to work (auto history field save)
            self.init_profile_metrics()

        res = Profile.objects.create(nickname=nickname, creation_date=creation_date,
                       modification_date=modification_date, weight=weight,
                       height=height, birth_date=birth_date, sex=sex, creator=creator,
                       work_score=work_score, moving_score=moving_score, sport_score=sport_score,
                       metabolism=metabolism, forced_base_calories=forced_base_calories)
        if auto_set_main_profile and creator is not None and creator.main_profile is None:
            creator.main_profile = res
            creator.save()
        return res

    def create_db_meta_planning(self, user=None, associate_to_user=True, with_n_days=None):
        if user is None:
            user = self.user
        metap = MetaPlanning.objects.create(user=user)
        if associate_to_user:
            user.meta_planning = metap
            user.save()
        if with_n_days is not None:
            for i in range(with_n_days):
                self.create_db_day(date = tz_aware(datetime.datetime(2007, 1, 1) + datetime.timedelta(days=i)).date(), user=user,
                                   add_to_meta=metap, planning=metap)
        return metap

    def _get_default_planning(self):
        if not hasattr(self, '_op_default_test_planning'):
            self._op_default_test_planning = self.create_db_planning(nb_days = 0)
        return self._op_default_test_planning

    def create_db_day(self, date=None, user=None, add_to_meta=None, creation_date=None, skipped=None,
                      shopping_list=None, planning=None, auto_create_planning=True):
        if user is None:
            user = self.user
        if planning is None and auto_create_planning:
            planning = self._get_default_planning()
        if date is None:
            date = timezone.now().date()
        elif type(date) is str:
            date = tz_aware(datetime.datetime.strptime(date, "%Y-%m-%d")).date()
        day = Day.objects.create(user=user, date=date, skipped=skipped, shopping_list=shopping_list, planning=planning)
        if creation_date:
            # Override creation date
            if isinstance(creation_date, datetime.date):
                creation_date = datetime.datetime.combine(creation_date, datetime.datetime.min.time())
            day.creation_date = make_aware(creation_date)
            day.save()
        if add_to_meta:
            add_to_meta.days.add(day)
        return day

    def create_db_planning(self, user=None, creation_date=None, modification_date=None, start_date=None, nb_days=7):
        """
        Creates 7 days in the database
        """
        if user is None:
            user = self.user
        if modification_date is None:
            modification_date = timezone.now()
        planning = Planning.objects.create(user=user, modification_date=modification_date)
        if creation_date is not None:
            planning.creation_date = creation_date
            planning.save()
        if modification_date is not None:
            planning.modification_date = modification_date
            planning.save()
        if nb_days == 0:
            return planning

        if start_date is None:
            start_date = datetime.date(2014, 3, 3) # Monday
        days = []
        for i in range(nb_days):
            day_date = start_date + datetime.timedelta(days=i)
            if type(day_date) is not datetime.date: day_date = day_date.date()
            day = Day.objects.create(user = user,
                                     modification_date   = modification_date,
                                     date = day_date, planning=planning)
            if creation_date is not None:
                day.creation_date = creation_date
                day.save()
            if modification_date is not None:
                day.modification_date = modification_date
                day.save()
            days.append(day)
        return planning

    def create_db_mealdishoption(self, meal_type, dish_type, min_speed_check = 1, min_budget_check=1, default_optional = False,
                                 default_recipe = None):
        return MealDishOption.objects.create(meal_type = meal_type, dish_type = dish_type,
                                             min_speed_check = min_speed_check,
                                             min_budget_check = min_budget_check,
                                             default_optional = default_optional,
                                             default_recipe = default_recipe)

    def get_default_mealplace(self):
        if self.places is None:
            self.places = dict((key, self.create_db_mealplace(key)) for key in ("home", "donoteat"))
        return self.places["home"]

    def create_db_mealplace(self, key = None):
        if key is None:
            key = "home"
        return MealPlace.objects.create(key = key)

    def create_db_mealtype(self, name = None, key = None, time = None,
                           nickname = None, dish_types = None, default_place = None, default_suggest = True,
                           force_suggest = None):
        try:                        nextId   = MealType.objects.latest('id').id + 1
        except ObjectDoesNotExist:  nextId   = 1
        if time is None:            time     = datetime.time(nextId % 24, 00)
        if name is None:            name     = "meal_type_%.2i" % nextId
        if key is None:             key = name
        if nickname is None:        nickname = name
        if force_suggest is None:   force_suggest = False
        if default_place is None:   default_place = self.get_default_mealplace()
        res = MealType.objects.create(name = name, nickname = nickname, time = time, default_place = default_place,
                                      default_suggest = default_suggest, force_suggest = force_suggest,
                                      key = key)
        if dish_types is not None:
            for dish_type in dish_types:
                self.create_db_mealdishoption(res, dish_type, min_budget_check = 3, min_speed_check = 3)
        return res

    def create_db_mealslot(self, day, time = datetime.time(12, 0), speed = 2, meal_type = None,
                           with_eaters = None, meal_place = None, suggest = True):
        if meal_type is None:   meal_type  = self.create_db_mealtype(time = time)
        if meal_place is None:  meal_place = self.get_default_mealplace()
        ms = MealSlot.objects.create(day            = day,
                                     time           = time,
                                     speed          = speed,
                                     meal_type      = meal_type,
                                     meal_place     = meal_place,
                                     suggest        = suggest)
        if with_eaters is None and hasattr(self, 'eaters'):
            with_eaters = self.eaters
        if with_eaters:
            for eater in with_eaters:
                MealSlotEater.objects.create(meal_slot=ms, eater=eater)
        return ms

    def create_db_eater(self, profile, user=None, regular=True):
        if user is None:
            user = self.user
        return Eater.objects.create(profile=profile, user=user, regular=regular)

    def create_db_taste(self, foodTag, profile = None, dislike = True):
        if profile is None:
            profile = self.profiles[-1]
        f = (5, -5)[dislike]
        return Taste.objects.create(profile = profile, food_tag = foodTag, fondness = f)

    def create_db_restricted_food(self, foodTag, profile = None):
        if profile is None:
            profile = self.profiles[-1]
        return RestrictedFood.objects.create(profile = profile, food_tag = foodTag)

    def create_db_rating(self, recipe, user, rating, comment=None, moderated_at='now'):
        if moderated_at == 'now':
            moderated_at = timezone.now()
        return RecipeRating.objects.create(recipe=recipe, user=user, rating=rating,
                                           comment=comment, moderated_at=moderated_at)

    def create_db_recipe_dislike(self, recipe, profile=None):
        if profile is None:
            profile = self.profiles[-1]
        return RecipeDislike.objects.create(profile=profile, recipe=recipe)

    def create_db_dish(self, meal_slot, dish_type, order=0, recipes=None, optional=False, user_dish_recipes=None):
        dish = Dish.objects.create(meal_slot=meal_slot, order=order,
                                   dish_type=dish_type, optional=optional)
        if recipes is not None:
            for recipe in recipes:
                self.create_db_dishrecipe(dish, recipe, user = user_dish_recipes)
        return dish

    def create_db_dishrecipe(self, dish, recipe, ratio=1., user=None, validated=False, order=1):
        return DishRecipe.objects.create(dish=dish, recipe=recipe, ratio=ratio,
                                         user=user, validated=validated, order=order)

    def create_db_information(self, title="BREAKING NEWS", content="plop", action="show_profile", valid_until=None):
        if valid_until is None:
            valid_until = timezone.now() + datetime.timedelta(days=1)

        return Information.objects.create(title=title, content=content, action=action,
                                          valid_until=valid_until)

    def create_db_problem(self, planning = None, enable_diet = False, dish_ids = None):
        if planning is None and hasattr(self, "planning"):
            planning = self.planning
        return Problem(self.planning, enable_diet = False, dish_ids = dish_ids)

    def create_db_config_stage(self, name = None, key = None, order = None, description = None):
        if order is None:
            try:                        order = ConfigStage.objects.latest('order').order + 1
            except ObjectDoesNotExist:  order = 1
        if key is None:                 key = "config_stage_%i" % order
        if name is None:                name = key
        if description is None:         description = ""
        return ConfigStage.objects.create(name = name, key = key, order = order, description = description)

    def create_db_config_completion(self, stage, user = None, date = None):
        if date is None:
            date = self.now
        if user is None:
            user = self.user
        return ConfigStageCompletion.objects.create(user = user, stage = stage, date = date)

    def create_db_subscription(self, start_date=None, user=None, level=2, end_date=None, nb_months=6, nb_days=0, trial_period_end=None,
                                     enabled=False, cancelled=False, discount=None, total_amount=None):
        if user is None:
            user = self.user
        if start_date is None:
            start_date = self.today
        if end_date is None:
            end_date = start_date
            end_date = add_months(end_date, nb_months)
            end_date = add_days(end_date, nb_days)
        if trial_period_end is None:
            trial_period_end = start_date + datetime.timedelta(days=14)
        if total_amount is None:
            total_amount = 10 * nb_months + 1 * nb_days
        return Subscription.objects.create(user=user, start_date=start_date, level=level, end_date=end_date,
                                           nb_days=nb_days, nb_months=nb_months, trial_period_end=trial_period_end,
                                           enabled=enabled, cancelled=cancelled, discount=discount,
                                           total_amount=total_amount)

    def create_db_publication(self, author, question = None, response = None, public = True, user_sex = True, user_date = None):
        if author is None:      author = self.user
        if question is None:    question = "Can you help ?"
        if response is None:    response = "Off course buddy !"
        if user_date is None:   user_date = self.today
        return Publication.objects.create(author = author, question = question, response = response, public = public, user_date = user_date, user_sex = user_sex)

    def create_db_transaction(self, subscription, created_at=None, ref=None, transaction_id=None, payment_type=None,
                                    price=999, ip=None, concluded_at=None, status=Transaction.STATUS_STARTED):

        if ref is None:
            ref = 'totoref'
        if ip is None:
            ip = '127.0.0.1'

        trans = Transaction.objects.create(subscription=subscription, ref=ref, transaction_id=transaction_id,
                                           payment_type=payment_type, price=price, ip=ip, concluded_at=concluded_at,
                                           status=status)

        if created_at is not None:
            trans.created_at = created_at
            trans.save()
        return trans

    def create_db_discussion(self, title = None, owner = None, dietician = None, closed = False, publication = None):
        if owner is None:
            owner = self.user
        if title is None:
            title = "Good question !"
        close_date = (None, timezone.now() + datetime.timedelta(minutes=1))[closed]
        return Discussion.objects.create(title = title, owner = owner, dietician = dietician, close_date = close_date, publication = publication)

    def create_db_message(self, discussion, content = None, author = None):
        if author is None:      author = self.user
        if content is None:     content = "Lorem ipsum"
        return Message.objects.create(discussion = discussion, author = author, content = content)

    def create_db_user_special_offer(self, discount, user=None, until=None):
        if user is None:
            user = self.user
        if until is None:
            until = today() + datetime.timedelta(days=2)
        return UserSpecialOffer.objects.create(user=user, discount=discount, until=until)

    def create_db_global_special_offer(self, start_date, end_date, discount=50, level=None):
        return GlobalSpecialOffer.objects.create(start_date=tz_aware(start_date), end_date=tz_aware(end_date),
                                                 discount=discount, level=level)
    def create_db_blog(self, user=None, **kargs):
        if user is None:
            user = self.user

        return Blog.objects.create(user=user, **kargs)

    @classmethod
    def get_fixture_path(cls, module_filename, fixture_file_name):
        """
        Return an absolute path to a fixture file.
        Must be called with __file__ as first argument

        Warning: only works in files starting by "test"

        self.get_fixture_path(__file__, "my_config_file.yml")
        """
        p = os.path.abspath(os.path.dirname(module_filename))
        # We start at django/my_app_name/tests/test_thingies/test_file.py"
        while os.path.split(p)[-1].startswith("test"):
            p = os.path.split(p)[0]

        # p is now django/my_app_name
        return os.path.join(p, "fixtures", fixture_file_name)

    def init_recipe_index(self, nutrient_ids):
        """
        (Re) load the recipe index, with given nutrient ids
        """
        with patch.object(Config, 'used_nutrient_ids', lambda: nutrient_ids):
            MainRecipeStorage.initialize(force=True)

    def assertMinMaxNumQueries(self, nb_min_queries, nb_max_queries, func):
        """
        Assert that the number of queries is between A and B
        """
        with self.assertNumQueries(FuzzyInt(nb_min_queries, nb_max_queries)):
            func()

    def is_authenticated(self, user = None):
        return self.access_token is not None

class OptalimTest(BaseOptalimTest):
    SUBSCRIPTION_LEVEL  = 0
    AUTH_APP = 'public'

    def create_db_user(self, *args, subscription_level = 0, auto_create_main_profile = False, **kargs):
        kargs['cls'] = User
        user = self._create_db_user(*args, **kargs)
        user.subscription_level = subscription_level
        user.save()
        if subscription_level > 0:
            # if subscription_level > 0, we create a subscription for this user
            self.create_db_subscription(level=subscription_level, enabled=True, user=user)
        if auto_create_main_profile:
            self.create_db_profile(nickname=kargs['name'], creator=user, auto_set_main_profile=True)
        return user

    def _create_default_user(self):
        self.user = self.create_db_user(email = self.MAIL, name = self.USERNAME,
                                        password = self.PASSWORD, roles = self.PERMISSIONS,
                                        subscription_level = self.SUBSCRIPTION_LEVEL)

class TestAPIWithLogin(OptalimTest):
    LOGIN_ON_STARTUP = True

class FuzzyInt(int):
    """
    Used for assertMinMaxNumQueries
    """
    def __new__(cls, lowest, highest):
        obj = super(FuzzyInt, cls).__new__(cls, highest)
        obj.lowest = lowest
        obj.highest = highest
        return obj

    def __eq__(self, other):
        return other >= self.lowest and other <= self.highest

    def __repr__(self):
        return "[%d..%d]" % (self.lowest, self.highest)

def add_permissions(*permissions):
    def decorator(method):
        """
        Decorator to add some permissions to the user during the test
        """
        def new_method(self, *args, **kargs):
            for permission in permissions:
                self.create_db_user_role(self.user, permission, creator = self.user)
            return method(self, *args, **kargs)
        update_wrapper(new_method, method)
        return new_method

    return decorator

def pgsql_only(fcn):
    """
    Decorator that enables only this test for pgsql
    """
    if 'postgresql' in optalim.settings.DATABASES['default']['ENGINE']:
        return fcn
    skipped_test = skip("skipped test because postgresql is not current database")
    update_wrapper(skipped_test, fcn)
    return skipped_test

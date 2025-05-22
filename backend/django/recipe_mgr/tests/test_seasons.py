from common.mock_tools      import fake_today_decorator, fake_redis_cache_decorator
from common.model           import reload_object
from common.test            import TestAPIWithLogin, add_permissions

from recipe_mgr.models      import FoodSeasonality
from recipe_mgr.seasons     import SeasonManager

import datetime

class SeasonalityTests(TestAPIWithLogin):
    
    def setUp(self):
        super().setUp()
        self.init_default_ingredient_settings()
        self.frozen = self.create_db_raw_state("frozen")
        
        self.carrot = self.create_db_food("carrot")
        self.strawberry = self.create_db_food("strawberry")
        self.chocolate = self.create_db_food("chocolateberry")
        
        self.carrot_season = self.create_db_food_seasonality(self.carrot.id, 11, 2) # November to February
        self.strawberry_season = self.create_db_food_seasonality(self.strawberry.id, 5, 9) # May to September
        
        self.all_seasons_recipe = self.create_db_recipe("yummy chocolate")
        self.create_db_ingredient(self.all_seasons_recipe, self.chocolate, 100)
        
        self.winter_carrots = self.create_db_recipe("shiny carrots")
        self.create_db_ingredient(self.winter_carrots, self.carrot, 100)
        
        self.frozen_strawberries = self.create_db_recipe("frozen strawberries")
        self.create_db_ingredient(self.frozen_strawberries, self.strawberry, 100, raw_state=self.frozen)
        
        self.cake_choco_strawberries = self.create_db_recipe("cake choco-strawberries")
        self.create_db_ingredient(self.cake_choco_strawberries, self.chocolate, 100)
        self.create_db_ingredient(self.cake_choco_strawberries, self.strawberry, 100) # Fresh strawberries
        
        
    def test_valid_monthes(self):
        self.assertEqual(self.strawberry_season.valid_monthes(), [5, 6, 7, 8, 9])
        self.assertEqual(self.carrot_season.valid_monthes(), [1, 2, 11, 12])
    
    
    @fake_today_decorator(2014, 7, 3)
    @fake_redis_cache_decorator
    def test_season_manager_in_summer(self):
        SeasonManager.update_all()
        season_dict = SeasonManager.seasonality_dict()
        
        expected_values = {
            self.all_seasons_recipe.id: True,
            self.frozen_strawberries.id: True,
            self.cake_choco_strawberries.id: True,
            self.winter_carrots.id: False
        }
        self.assertEqual(season_dict, expected_values)
        
    @fake_today_decorator(2014, 12, 3)
    @fake_redis_cache_decorator
    def test_season_manager_in_winter(self):
        SeasonManager.update_all()
        season_dict = SeasonManager.seasonality_dict()
        
        expected_values = {
            self.all_seasons_recipe.id: True,
            self.frozen_strawberries.id: True,
            self.cake_choco_strawberries.id: False,
            self.winter_carrots.id: True
        }
        self.assertEqual(season_dict, expected_values)
        
        
    def test_season_food_api_get(self):
        response = self.client.get('/secure/api/food/%i/seasonality' % self.strawberry.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"status": "season", "start_month": 5, "end_month": 9})
        
        response = self.client.get('/secure/api/food/%i/seasonality' % self.chocolate.id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"status": "no_season"})
        
        
    @add_permissions("admin")
    def test_season_food_api_set(self):
        response = self.client.post('/secure/api/food/%i/set_seasonality' % self.strawberry.id, {"start_month": 1, "end_month": 3})
        self.assertEqual(response.status_code, 200)
        reload_object(self.strawberry_season)
        self.assertEqual(self.strawberry_season.start_month, 1)
        self.assertEqual(self.strawberry_season.end_month, 3)
        
        response = self.client.post('/secure/api/food/%i/set_seasonality' % self.chocolate.id, {"start_month": 6, "end_month": 7})
        self.assertEqual(response.status_code, 200)
        obj = FoodSeasonality.objects.get(food=self.chocolate)
        self.assertEqual(obj.start_month, 6)
        self.assertEqual(obj.end_month, 7)
        
    @add_permissions("admin")
    def test_season_food_api_set_delete(self):
        response = self.client.post('/secure/api/food/%i/set_seasonality' % self.strawberry.id, {"start_month": 1, "end_month": 12})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(FoodSeasonality.objects.filter(food=self.strawberry).count(), 0) # No more season
        
        
    def test_search_food_api(self):
        """
        Food search API with seasons
        """
        response = self.client.get('/api/food/search/berry', {'with_season': True})
        self.assertEqual(response.status_code, 200)
        res = dict((food['name'], food['seasonal']) for food in response.data['foods'])
        self.assertEqual(res,
                         {'chocolateberry': False,
                          'strawberry': True})
                         
    @fake_today_decorator(2014, 7, 3)
    @fake_redis_cache_decorator
    def test_seasonal_recipes_selection(self):
        """
        Suuummer time. 3 recipes are seasonal :
        - yummy chocolate
        - frozen strawberries
        - cake choco-strawberries
        """
        
        # "yummy chocolate" and "cake choco-strawberries" have more than 4 ingredients
        
        for i in range(4):
            food = self.create_db_food("some_food_%i" % i)
            self.create_db_ingredient(self.cake_choco_strawberries, food, 100)
            self.create_db_ingredient(self.all_seasons_recipe, food, 100)
        
        SeasonManager.update_all()
        
        # Only the cake has a photo
        self.cake_choco_strawberries.auto_photo = False
        self.cake_choco_strawberries.save()
        
        response = self.client.get('/api/recipe/random_season_selection')
        self.assertEqual(response.status_code, 200)
        recipe_ids = set()
        for recipe in response.data["results"]:
            recipe_ids.add(recipe["id"])
        
        self.assertEqual(recipe_ids, set([self.cake_choco_strawberries.id, ]))
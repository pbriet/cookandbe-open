from common.test                import TestAPIWithLogin
from planning_mgr.models        import NotNow, Day, DishRecipe
import datetime

class TestNotNow(TestAPIWithLogin):
    
    SUBSCRIPTION_LEVEL = 1

    def setUp(self):
        super().setUp()
        self.recipe1 = self.create_db_recipe()
        self.recipe2 = self.create_db_recipe()
        
        self.other_user = self.create_db_user("other@other.fr")

        self.date = datetime.date.today()
        self.day = self.create_db_day(self.date)
        
        # Creating a not now for another user
        NotNow.objects.create(user=self.other_user, recipe=self.recipe1)

    def test_add_not_now(self):
        response = self.client.post("/api/user/%i/not_now/%i" % (self.user.id, self.recipe1.id))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(NotNow.objects.filter(user=self.user).count(), 1)
        
        response = self.client.post("/api/user/%i/not_now/%i" % (self.user.id, self.recipe2.id))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(NotNow.objects.filter(user=self.user).count(), 2)
    
    def _init_dish(self):
        meal_slot = self.create_db_mealslot(self.day)
        dish_type = self.create_db_dishtype()
        dish      = self.create_db_dish(meal_slot, dish_type)
        
        # Created a validated and forced dishrecipe
        d = self.create_db_dishrecipe(dish, self.recipe2, user=self.user, validated=True)
        
        return dish
    
    def test_set_recipe_deletes_not_now(self):
        
        # Create a dish with recipe2 inside
        dish = self._init_dish()
        
        # NotNow on recipe1 and recipe2
        for recipe in (self.recipe1, self.recipe2):
            NotNow.objects.create(recipe=recipe, user=self.user)
        
        # Forcing recipe1 on dish
        response = self.client.post("/api/user/%i/set_dishrecipe/%i" % (self.user.id, dish.id), {'recipe_id': self.recipe1.id})
        self.assertEqual(response.status_code, 201)
        
        # Recipe1 should have been removed from this user not nows
        self.assertEqual(NotNow.objects.filter(user=self.user).count(), 1)
        self.assertEqual(NotNow.objects.get(user=self.user).recipe.id, self.recipe2.id)
        
        
    def test_not_now_on_locked_dish(self):
        
        dish = self._init_dish()

        # Calling not now, and giving the dish as an argument
        # First calling not now on the wrong recipe -> should have no effect
        # Then calling it with the correct recipe -> dishrecipe should be "unlocked"
        for recipe in self.recipe1, self.recipe2:
            response = self.client.post("/api/user/%i/not_now/%i" % (self.user.id, recipe.id), {'dish_id': dish.id})
            self.assertEqual(response.status_code, 201)
            
            self.assertTrue(DishRecipe.objects.count(), 1)
            dr = DishRecipe.objects.get()
            if recipe == self.recipe1:
                # Unaffected
                self.assertEqual(dr.user_id, self.user.id)
                self.assertEqual(dr.validated, True)
            else:
                # Unlocked
                self.assertEqual(dr.user_id, None)
                self.assertEqual(dr.validated, False)
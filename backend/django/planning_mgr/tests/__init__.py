import datetime

class TestWithFilledPlanning(object):
    """
    Test that initiates a planning with some real content in it : day, mealslots, dishes, recipes
    """
    def init_day(self, day):
        self.day = day
        self.init_default_ingredient_settings()
        self.init_db_profile_eater()

        self.dish_type = self.create_db_dishtype()

        self.meal_type1 = self.create_db_mealtype("Midi")
        self.meal_type2 = self.create_db_mealtype("Soir")

        self.meal_slot1 = self.create_db_mealslot(self.day, meal_type = self.meal_type1, time=datetime.time(12, 0))
        self.meal_slot2 = self.create_db_mealslot(self.day, meal_type = self.meal_type2, time=datetime.time(20, 0))

        self.dish1 = self.create_db_dish(self.meal_slot1, self.dish_type)
        self.dish2_1 = self.create_db_dish(self.meal_slot2, self.dish_type)
        self.dish2_2 = self.create_db_dish(self.meal_slot2, self.dish_type)

        self.recipe1 = self.create_db_recipe("recipe1")
        self.recipe2 = self.create_db_recipe("Canard à l'orange")
        self.recipe3 = self.create_db_recipe("recipe3")

        self.create_db_dishrecipe(self.dish1, self.recipe1, ratio=2)
        self.create_db_dishrecipe(self.dish2_1, self.recipe2, order=2)
        self.create_db_dishrecipe(self.dish2_1, self.recipe3)

        non_fresh_food_type = self.create_db_foodtype("non-fresh", usually_stored=True)

        self.carrots = self.create_db_food("carrots")
        self.chocolate = self.create_db_food("chocolate", food_type=non_fresh_food_type)

        default_carrot_conversion = self.create_db_food_conversion(self.carrots)
        default_choco_conversion = self.create_db_food_conversion(self.chocolate)

        self.chocolate_chunk_cnv = self.create_db_food_conversion(self.chocolate, "chunk", 10, plural="chunks")
        self.small_carrot_cnv = self.create_db_food_conversion(self.carrots, "small", 100)
        self.big_carrot_cnv = self.create_db_food_conversion(self.carrots, "big", 200)
        
        # Recipe 1 is 2 big carrots and 1 chocolate chunk  (RATIO=2)
        self.ing1_1 = self.create_db_ingredient(self.recipe1, self.carrots, 400, default_conversion=default_carrot_conversion)
        self.ing1_2 = self.create_db_ingredient(self.recipe1, self.chocolate, 10, default_conversion=default_choco_conversion)

        # Recipe 2 is 1 small carrot and 5 chocolate chunks (RATIO=1)
        self.ing2_1 = self.create_db_ingredient(self.recipe2, self.carrots, 100, default_conversion=default_carrot_conversion)
        self.ing2_2 = self.create_db_ingredient(self.recipe2, self.chocolate, 50, default_conversion=default_choco_conversion)

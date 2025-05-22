from django.core.management.base                import CommandError
from common.test                                import OptalimTest
from django.utils                               import timezone
from nutrient.models                            import FoodNutrient, Nutrient
from recipe_mgr.management.commands.clonefood   import Command as CloneFood
from recipe_mgr.models                          import Food, FoodType,\
                                                       FoodConversion, FoodSeasonality,\
                                                       FoodTag


class TestCloneFood(OptalimTest):
    """
    Test of "manage.py clonefood" command
    """
    def setUp(self):
        OptalimTest.setUp(self)
        self.init_default_ingredient_settings()

        self.food_type     = self.create_db_foodtype("cake type")
        self.food          = self.create_db_food("old")
        self.nutrient      = self.create_db_nutrient()
        self.food_nutrient = self.create_db_foodnutrient(self.food, self.nutrient, 100)

        self.conversion = self.create_db_food_conversion(self.food, "fruit")

        self.tags = [self.create_db_food_tag("cake tag"), self.create_db_food_tag("sweet")]

        self.season = FoodSeasonality.objects.create(food=self.food, start_month=3, end_month=8)

    def test_clone_food(self):
        CloneFood().handle(self.food.id, "newnamee")

        self.assertEqual(Food.objects.count(), 2)
        self.assertEqual(sorted([f.name for f in Food.objects.all()]), ["newnamee", "old"])
        self.assertEqual(Nutrient.objects.count(), 1)
        self.assertEqual(FoodNutrient.objects.count(), 2)
        self.assertEqual(FoodType.objects.count(), 1)
        self.assertEqual(FoodTag.objects.count(), 2)
        self.assertEqual(FoodConversion.objects.count(), 2)
        self.assertEqual(FoodSeasonality.objects.count(), 2)

        new_food = Food.objects.get(name="newnamee")
        self.assertEqual(new_food.parent.id, self.food.id)

    def test_invalid_id(self):
        self.assertRaises(CommandError, CloneFood().handle, "toto", "newname")

    def test_invalid_nb_args(self):
        self.assertRaises(CommandError, CloneFood().handle, 2, "newname", 7)
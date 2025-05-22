from common.test                    import OptalimTest
from mock                           import patch, call

from recipe_mgr.controller          import RecipeImageGenerator

import storages.backends.s3boto3

class TestRecipeImageGeneration(OptalimTest):

    def setUp(self):
        super().setUp()
        self.init_default_ingredient_settings()
        self.recipe = self.create_db_recipe()
        self.food1 = self.create_db_food()
        self.food2 = self.create_db_food("asparagus")
        self.food3 = self.create_db_food()

        # Recipe has two main ingredients and a very small one
        ingredient1 = self.create_db_ingredient(self.recipe, self.food1, 100)
        ingredient2 = self.create_db_ingredient(self.recipe, self.food2, 1)
        ingredient3 = self.create_db_ingredient(self.recipe, self.food3, 50)

    def build_food_tags(self):

        self.food_tag1 = self.create_db_food_tag("tag1", foods=[self.food1])
        self.food_tag2 = self.create_db_food_tag("asparagus", foods=[self.food2])
        self.food_tag3 = self.create_db_food_tag("tag3", foods=[self.food3])
        self.food_tag4 = self.create_db_food_tag("thing", foods=[])
        # This food tag is parent of food tag 3
        self.food_tag_parent = self.create_db_food_tag("tag_parent")
        self.food_tag_parent.children.add(self.food_tag3)

    def set_photo(self, food_tag):
        food_tag.photo = "/home/toto/" + food_tag.name + ".jpg"
        food_tag.save()

    @patch('recipe_mgr.controller.RecipeImageGenerator.build_image')
    def _test_pick_best_photo(self, expected_food_tags, mock_build_image):
        generator = RecipeImageGenerator(self.recipe.id)
        generator()

        if expected_food_tags is None:
            self.assertFalse(mock_build_image.called)
            return

        self.assertTrue(mock_build_image.called)
        args, kwargs = mock_build_image.call_args

        food_tags = args[1]
        for food_tag in food_tags:
            print("* ", food_tag.name)
        self.assertEqual(len(food_tags), len(expected_food_tags))
        for tag, expected in zip(food_tags, expected_food_tags):
            self.assertEqual(tag.id, expected.id)

    def test_with_no_food_tag(self):
        """
        Test that there is no way to build a photo if ingredients have no food tags
        """
        self._test_pick_best_photo(None)

    def test_with_food_tag_without_photo(self):
        """
        Test that there is no way to build a photo if food tags have no.. photo
        """
        self.build_food_tags()
        self._test_pick_best_photo(None)

    def test_select_two_with_photo(self):
        """
        Test that the 2 main ingredients are selected (the parent having no photo)
        """
        self.build_food_tags()
        for tag in (self.food_tag1, self.food_tag2, self.food_tag3):
            self.set_photo(tag)
        self._test_pick_best_photo([self.food_tag1, self.food_tag3])

    def test_select_two_with_parent_photo(self):
        """
        Test that the 2 main ingredients are selected (the parent having a photo, and not food_tag3)
        """
        self.build_food_tags()
        for tag in (self.food_tag1, self.food_tag2, self.food_tag_parent):
            self.set_photo(tag)
        self._test_pick_best_photo([self.food_tag1, self.food_tag_parent])


    def test_select_title_and_ingredient(self):
        """
        One food tag from the title, and one from the ingredient
        """
        self.build_food_tags()
        for tag in (self.food_tag1, self.food_tag2):
            self.set_photo(tag)
        self.recipe.name = "thing with asparagus in it"
        self.recipe.save()
        self._test_pick_best_photo([self.food_tag2, self.food_tag1])

    def test_do_not_select_title_food_tag_if_not_ingredient(self):
        """
        test that a food tag detected in the recipe title is not picked if it's not one of the ingredient
        """
        self.build_food_tags()
        for tag in (self.food_tag4,):
            self.set_photo(tag)
        self.recipe.name = "thing with asparagus in it"
        self.recipe.save()
        self._test_pick_best_photo(None)


    @patch('django.db.models.fields.files.ImageFieldFile.delete')
    def test_auto_recipe_img_deletion(self, mock_delete):
        """
        Checks that the deletion of a recipe implies the deletion of its image in storage
        """
        self.recipe.photo = "/home/toto/plop.jpg"
        self.recipe.save()

        self.recipe.delete()

        mock_delete.assert_called_once()
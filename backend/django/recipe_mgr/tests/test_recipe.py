from common.test                        import TestAPIWithLogin, add_permissions, OptalimTest
from common.model                       import reload_object
from planning_mgr.models                import Dish
from recipe_mgr.models                  import CookingMethod, DishType, RecipeDishType, Recipe
from recipe_mgr.models                  import Food, RecipeInstruction, Ingredient
from recipe_mgr.models                  import Ustensil, RecipeTag
from user_mgr.models                    import User
from mock                               import patch, MagicMock
from optalim.config                     import Config
import copy
import json

import storages.backends.s3boto3

class TestRecipeBase(OptalimTest):
    TAGS = 7
    USTENSILS = 5
    DISH_TYPES = 6
    INGREDIENTS = 4
    INSTRUCTIONS = 2
    INITIALIZE_RECIPE_INDEXER = True

    def setUp(self):
        super().setUp()
        self.init_default_ingredient_settings()
        # Many2many attributes
        ustensils = [self.create_db_ustensil() for j in range(self.USTENSILS)]
        dish_types = [self.create_db_dishtype() for k in range(self.DISH_TYPES)]
        tags = [self.create_db_recipe_tag() for l in range(self.TAGS)]
        # Simple attributes
        self.default_values = {
            "name": "test recipe",
            "author": self.user,
            "status": 1,
            "price": 2,
            "difficulty": 3,
            "nb_people": 5,
            "prep_minutes": 12,
            "cook_minutes": 13,
            "rest_minutes": 14,
            "internal": True
        }
        # Recipe
        self.orig = self.create_db_recipe(ustensils = ustensils, dish_types = dish_types, tags = tags, **self.default_values)
        self.orig.photo = "/path/to/photo_%i.png" % self.orig.id
        self.orig.save()
        # Special many2many attributes
        for i in range(self.INGREDIENTS):
            food = self.create_db_food()
            self.create_db_ingredient(self.orig, food = food, grams = 10 * i + 10)
        for m in range(self.INSTRUCTIONS):
            self.create_db_instruction(self.orig, "Instruction %i" % m)

    def _check_db_clone_objects(self, ratio):
        # Clone independant
        self.assertEqual(RecipeTag.objects.count(), self.TAGS)
        self.assertEqual(Food.objects.count(), self.INGREDIENTS)
        self.assertEqual(Ustensil.objects.count(), self.USTENSILS)
        self.assertEqual(DishType.objects.count(), self.DISH_TYPES)
        # Clone dependant
        self.assertEqual(Recipe.objects.count(), ratio)
        self.assertEqual(Ingredient.objects.count(), ratio * self.INGREDIENTS)
        self.assertEqual(RecipeDishType.objects.count(), ratio * self.DISH_TYPES)
        self.assertEqual(RecipeInstruction.objects.count(), ratio * self.INSTRUCTIONS)
        # Attributes
        for recipe in Recipe.objects.all():
            # Simple
            for attr, value in self.default_values.items():
                self.assertEqual(getattr(recipe, attr), value)
            # Many2many
            self.assertEqual(recipe.tags.count(), self.TAGS)
            self.assertEqual(recipe.ustensils.count(), self.USTENSILS)
            self.assertEqual(recipe.dish_types.count(), self.DISH_TYPES)
            self.assertEqual(recipe.ingredients.count(), self.INGREDIENTS)
            self.assertEqual(recipe.instructions.count(), self.INSTRUCTIONS)


    @patch('django.db.models.fields.files.FieldFile.save')
    def test_clone_recipe(self, mock_save):
        self._check_db_clone_objects(1)
        self.orig.photo.file = "fake_file_content"
        clone = Recipe.clone(self.orig)
        self.assertTrue(self.orig.pk != clone.pk)
        self.assertTrue(self.orig.id != clone.id)
        self._check_db_clone_objects(2)
        mock_save.assert_called_once()

class TestRecipeAPI(TestAPIWithLogin):
    INITIALIZE_RECIPE_INDEXER = True
    def setUp(self):
        super().setUp()
        self.recipes = [
            self.create_db_recipe(name=name)
            for name in ('recipe 0', 'recipe 1', 'recipe 2', 'recipe 3', 'recipe 4')]

        # Recipe 4 has been written by somebody else
        self.user2 = User.objects.create_user('somebody_else', password='test')
        self.recipes[-1].author = self.user2
        self.recipes[-1].save()

        self.breakfast = self.create_db_dishtype("breakfast")
        self.starter = self.create_db_dishtype("starter")

        self.my_tag = self.create_db_recipe_tag()

        # Some ustensils
        self.ustensil = self.create_db_ustensil("Luce Tancile")

        # Recipe 0 and 1 are some starters
        for i in (0, 1):
            RecipeDishType.objects.create(recipe=self.recipes[i], dish_type=self.starter)

        # Recipe 2 is a breakfast
        RecipeDishType.objects.create(recipe=self.recipes[2], dish_type=self.breakfast)

        # Recipe 3 can be either a breakfast or a starter
        RecipeDishType.objects.create(recipe=self.recipes[3], dish_type=self.breakfast)
        RecipeDishType.objects.create(recipe=self.recipes[3], dish_type=self.starter)

        # Recipe 4 is "nothing" (for testing purpose)


    def test_count_recipes(self):
        """
        Tests of /api/recipe/count
        """
        response = self.client.get('/api/recipe/count')
        self.assertEqual(response.status_code, 403)

        response = self.client.get('/secure/api/recipe/count')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"result": 5})

        response = self.client.get('/secure/api/recipe/count', {'dimension': 'dish_types'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"result": {self.breakfast.id: 2, self.starter.id: 3}})

        response = self.client.get('/secure/api/recipe/count', {'author_id': self.user.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"result": 4})

        response = self.client.get('/secure/api/recipe/count', {'dimension': 'author'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data, {"result": {self.user.id: 4, self.user2.id: 1}})


    def test_get_recipes(self):
        """
        Getting all recipes.
        """
        response = self.client.get('/api/recipe')
        self.assertEqual(response.status_code, 200)
        self.assertEqual(sorted([d['name'] for d in response.data]), ['recipe 0', 'recipe 1', 'recipe 2', 'recipe 3', 'recipe 4'])

    def test_get_many_recipes(self):
        """
        Test getting a selection of recipes by id
        """
        response = self.client.get('/api/recipe/get_many', {'ids': [self.recipes[1].id, self.recipes[3].id],
                                                            'serializer': 'full'})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(sorted([d['name'] for d in response.data]), ['recipe 1', 'recipe 3'])

    def test_get_recipes_by_dish_type(self):
        """
        Getting all recipes of one given dish type
        """
        response = self.client.get('/api/recipe', {'dish_type_id': self.breakfast.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(sorted([d['name'] for d in response.data]), ['recipe 2', 'recipe 3'])

    def test_get_recipes_by_author(self):
        """
        Getting all recipes of one given author
        """
        response = self.client.get('/api/recipe', {'author_id': self.user2.id})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(sorted([d['name'] for d in response.data]), ['recipe 4'])

    def test_get_dishtypes(self):
        """
        Getting dishtypes of one recipe
        """
        response = self.client.get('/api/recipe/%s/dish_types' % self.recipes[3].id)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(sorted([d['name'] for d in response.data]), ['breakfast', 'starter'])

    def test_add_dishtype(self):
        """
        Adding "breakfast" dish_type to recipes[3]
        """
        response = self.client.post('/api/recipe/%s/add_dish_type' % self.recipes[0].id,
                                    json.dumps({"dish_type_id": self.breakfast.id}),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 200)

        recipe = Recipe.objects.get(pk=self.recipes[0].id)
        self.assertEqual(sorted([d.name for d in recipe.dish_types.all()]), ['breakfast', 'starter'])

    def test_add_dishtype_invalid(self):
        """
        Invalid input for add_dish_type
        """
        INPUTS = [
            {"dish_type_id": 99999},
            {"dish_type_id": "lolwat"},
            {},
            {"invalid_key": 1}]

        for _input in INPUTS:
            response = self.client.post('/api/recipe/%s/add_dish_type' % self.recipes[3].id,
                                        json.dumps(_input), content_type="application/json")
            self.assertEqual(response.status_code, 400)


    def test_add_dishtype_duplicate(self):
        """
        Test adding breakfast again on recipes[2]
        """
        response = self.client.post('/api/recipe/%s/add_dish_type' % self.recipes[2].id,
                                    json.dumps({"dish_type_id": self.breakfast.id}),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 200)

        recipe = Recipe.objects.get(pk=self.recipes[2].id)
        self.assertEqual([d.name for d in recipe.dish_types.all()], ['breakfast'])

    # def test_cannot_remove_unique_dishtype(self):
    #     """
    #     Test that removing a unique dish_type generates a failure
    #     """
    #     response = self.client.post('/api/recipe/%s/remove_dish_type' % self.recipes[2].id,
    #                                 json.dumps({"dish_type_id": self.breakfast.id}),
    #                                 content_type="application/json")
    #     self.assertEqual(response.status_code, 400)

    #     recipe = Recipe.objects.get(pk=self.recipes[2].id)
    #     self.assertEqual([d.name for d in recipe.dish_types.all()], ['breakfast'])


    def test_remove_dishtype(self):
        """
        Test successful removal of a dish_type, with previous dishrecipe set on it
        """
        # Adding a second dish_type to recipe2
        RecipeDishType.objects.create(recipe=self.recipes[2], dish_type=self.starter)

        # Creating a dishrecipe with recipe2, that is a breakfast
        day = self.create_db_day()
        meal_slot = self.create_db_mealslot(day)
        dish = self.create_db_dish(meal_slot, self.breakfast, recipes=[self.recipes[2]])

        response = self.client.post('/api/recipe/%s/remove_dish_type' % self.recipes[2].id,
                                    json.dumps({"dish_type_id": self.breakfast.id}),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 200)

        recipe = Recipe.objects.get(pk=self.recipes[2].id)
        self.assertEqual([d.name for d in recipe.dish_types.all()], ["starter"])

        # Dishtype of the dish must have changed !
        reload_object(dish)
        self.assertEqual(dish.dish_type.name, "starter")
        self.assertTrue(dish.dishrecipe_set.count(), 1) # Still recipe2


    def test_remove_dishtype_aggregated(self):
        dish_type_agg, dish_type1, dish_type2 = self.create_db_dishtype_aggregated()

        recipe = self.create_db_recipe("recipe1", dish_types=[dish_type1, dish_type_agg])

        day = self.create_db_day()
        meal_slot = self.create_db_mealslot(day)
        # Dish is aggregated, and contains one recipe, which is aggregated
        dish = self.create_db_dish(meal_slot, dish_type=dish_type_agg, recipes=[recipe])

        # We remove dish_type_agg from recipe. It is now a non-aggregated dish_type
        response = self.client.post('/api/recipe/%s/remove_dish_type' % recipe.id,
                                    json.dumps({"dish_type_id": dish_type_agg.id}),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 200)

        self.assertEqual(Dish.objects.count(), 1)
        new_dish = Dish.objects.get()
        self.assertEqual(new_dish.id, dish.id) # No new object

        # Dish should now have dish_type 1 instead of aggregated
        self.assertEqual(new_dish.dish_type_id, dish_type1.id)


    def test_remove_dishtype_on_aggregated(self):
        """
        Test that removing a dishtype on a recipe which is as part of an existing aggregated dish, splitted
        the dish into multiple dishes with correct dish_types.
        """
        dish_type_agg, dish_type1, dish_type2 = self.create_db_dishtype_aggregated()
        another_dish_type = self.create_db_dishtype("another_dishtype")

        # recipe1 has dish_type1 and another_dishtype
        # recipe2 has dish_type2
        recipe1 = self.create_db_recipe("recipe1", dish_types=[dish_type1, another_dish_type])
        recipe2 = self.create_db_recipe("recipe2", dish_types=[dish_type2])

        day = self.create_db_day()
        meal_slot = self.create_db_mealslot(day)
        # recipe1 and recipe2 are in the same dish, which is an aggregated one (dt1 + dt2)
        dish = self.create_db_dish(meal_slot, dish_type=dish_type_agg, recipes=[recipe1, recipe2])

        # We remove dish_type1 from recipe1
        response = self.client.post('/api/recipe/%s/remove_dish_type' %recipe1.id,
                                    json.dumps({"dish_type_id": dish_type1.id}),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 200)

        # Now there should be two dishes, with dish_types : [another_dish_type, dish_type2]
        self.assertEqual(Dish.objects.count(), 2)
        self.assertEqual(Dish.objects.filter(pk=dish.id).count(), 0) # The old dish must have been deleted
        dishes = Dish.objects.all().order_by('order')
        self.assertEqual(dishes[0].dish_type_id, another_dish_type.id)
        self.assertEqual(dishes[0].order, 0)
        self.assertEqual(dishes[0].meal_slot_id, meal_slot.id)
        self.assertEqual(dishes[0].dishrecipe_set.count(), 1)
        self.assertEqual(dishes[0].dishrecipe_set.get().recipe_id, recipe1.id)

        self.assertEqual(dishes[1].dish_type_id, dish_type2.id)
        self.assertEqual(dishes[1].order, 1)
        self.assertEqual(dishes[1].meal_slot_id, meal_slot.id)
        self.assertEqual(dishes[1].dishrecipe_set.count(), 1)
        self.assertEqual(dishes[1].dishrecipe_set.get().recipe_id, recipe2.id)



    def test_add_remove_tag(self):
        """
        Simple test of adding and removing a tag
        """
        response = self.client.post('/api/recipe/%s/add_tag' % self.recipes[3].id,
                                    json.dumps({"tag_id": self.my_tag.id}),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 200)

        recipe = Recipe.objects.get(pk=self.recipes[3].id)
        self.assertEqual([t.name for t in recipe.tags.all()], ['awesome tag'])

        response = self.client.post('/api/recipe/%s/remove_tag' % self.recipes[3].id,
                                    json.dumps({"tag_id": self.my_tag.id}),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 200)

        recipe = Recipe.objects.get(pk=self.recipes[3].id)
        self.assertEqual(recipe.tags.count(), 0)


    def _get_default_recipe_values(self):
        values = {'price': 3,
                             'difficulty': 3,
                             'prep_minutes' : 10,
                             'cook_minutes': 120,
                             'nb_people': 2,
                             'name': "My new recipe",
                             'author': self.user.id,
                             }
        return copy.copy(values)


    def test_create_recipe(self):
        """
        Creating a recipe through the API
        """
        recipe_values = self._get_default_recipe_values()
        response = self.client.post('/api/recipe', recipe_values)
        self.assertEqual(response.status_code, 201)

        recipe = Recipe.objects.get(name="My new recipe")
        for key, value in recipe_values.items():
            if key == 'author': key = 'author_id'
            self.assertEqual(getattr(recipe, key), value)

    def test_create_invalid_recipe(self):
        recipe_values = self._get_default_recipe_values()

        for key, invalid_value in (('price', 0),
                                  ('price', 99),
                                  ('difficulty', 0),
                                  ('difficulty', 102),
                                  ('prep_minutes', -1),
                                  ('prep_minutes', 9999),
                                  ('cook_minutes', -1),
                                  ('cook_minutes', 9999),
                                  ('rest_minutes', -1),
                                  ('rest_minutes', 9999),
                                  ('nb_people', 0),
                                  ('nb_people', 25)):
            inv_values = copy.copy(recipe_values)
            inv_values[key] = invalid_value
            response = self.client.post('/api/recipe', inv_values)
            self.assertEqual(response.status_code, 400)

    def test_ustensil(self):
        # Add ustensil
        response = self.client.post('/api/recipe/%s/add_ustensil' % self.recipes[3].id,
                                    json.dumps({"ustensil_id": self.ustensil.id}),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 200)
        recipe = Recipe.objects.get(pk=self.recipes[3].id)
        self.assertEqual(list(recipe.ustensils.all()), [self.ustensil])

        # Add ustensil duplicate
        response = self.client.post('/api/recipe/%s/add_ustensil' % self.recipes[3].id,
                                    json.dumps({"ustensil_id": self.ustensil.id}),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 200)
        recipe = Recipe.objects.get(pk=self.recipes[3].id)
        self.assertEqual(list(recipe.ustensils.all()), [self.ustensil])

        # Remove ustensil
        response = self.client.post('/api/recipe/%s/remove_ustensil' % self.recipes[3].id,
                                    json.dumps({"ustensil_id": self.ustensil.id}),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 200)
        recipe = Recipe.objects.get(pk=self.recipes[3].id)
        self.assertEqual(list(recipe.ustensils.all()), list())

        # Remove ustensil
        response = self.client.post('/api/recipe/%s/remove_ustensil' % self.recipes[3].id,
                                    json.dumps({"ustensil_id": self.ustensil.id}),
                                    content_type="application/json")
        self.assertEqual(response.status_code, 200)
        recipe = Recipe.objects.get(pk=self.recipes[3].id)
        self.assertEqual(list(recipe.ustensils.all()), list())

class TestRecipeAPIWithNutrients(TestAPIWithLogin):
    INITIALIZE_RECIPE_INDEXER = True
    def setUp(self):
        super().setUp()
        self.init_default_ingredient_settings()

        dish_type = self.create_db_dishtype()

        self.recipe1 = self.create_db_recipe("recipe1", dish_types=[dish_type])
        self.recipe2 = self.create_db_recipe("recipe2", dish_types=[dish_type])
        self.carrots = self.create_db_food('carrots')
        # 100g of carrots in the recipe 1, 50g in recipe2
        self.create_db_ingredient(self.recipe1, self.carrots, 100)
        self.create_db_ingredient(self.recipe2, self.carrots, 50)
        self.nutrient1 = self.create_db_nutrient("nutri1")
        self.nutrient2 = self.create_db_nutrient("nutri2")

        # 5g of nutri1 per g of carrots
        self.create_db_foodnutrient(self.carrots, self.nutrient1, 5)
        self.create_db_foodnutrient(self.carrots, self.nutrient2, 3)

        # Initializing recipeIndex
        self.init_recipe_index([self.nutrient1.id, self.nutrient2.id])

    def _check_nutrient_values(self, response, nutrient_id, value1, value2):
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data), 2)
        self.assertEqual(response.data[0]['nutrients'][nutrient_id], value1)
        self.assertEqual(response.data[1]['nutrients'][nutrient_id], value2)

    @add_permissions("admin")
    def test_one_nutrient(self):
        response = self.client.get('/api/recipe', {'nutrient_ids': [self.nutrient1.id]})
        self._check_nutrient_values(response, self.nutrient1.id, 500, 250)
        self.assertEqual(len(response.data[0]['nutrients']), 1)
        self.assertEqual(len(response.data[1]['nutrients']), 1)

    @add_permissions("admin")
    def test_two_nutrients(self):
        response = self.client.get('/api/recipe', {'nutrient_ids': [self.nutrient1.id, self.nutrient2.id]})
        self._check_nutrient_values(response, self.nutrient1.id, 500, 250)
        self._check_nutrient_values(response, self.nutrient2.id, 300, 150)
        self.assertEqual(len(response.data[0]['nutrients']), 2)
        self.assertEqual(len(response.data[1]['nutrients']), 2)

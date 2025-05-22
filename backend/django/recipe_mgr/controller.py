from django.db.models           import Count
from django.core.files          import File
from math                       import ceil
from PIL                        import Image

import io

from recipe_mgr.models          import Recipe, FoodTag
from recipe_mgr.serializers     import RatioRecipeSerializer

def get_full_recipe_serialization(query_args, ratio=None, many=False):
    """
    Retrieve the recipe, and returns its fully serialized version,
    including ingredients
    """
    recipes = list(Recipe.objects.select_related('author__blog').prefetch_related(
        'ingredients__raw_state',
        'ingredients__default_conversion',
        'ingredients__food__conversions',
        'ustensils',
        'instructions',
        'tags',
        'dish_types',
        'dishrecipe_set'
    ).filter(**query_args))
    if not many :
        if len(recipes) == 0:
            return None
        assert len(recipes) == 1
        return RatioRecipeSerializer(recipes[0], ratio, with_blog=True).data

    res = [RatioRecipeSerializer(r, ratio, with_blog=True).data for r in recipes]
    return res

class RecipeImageGenerator(object):
    # Auto-generate a recipe image from its food tags

    def __init__(self, recipe_id):
        self.recipe_id = recipe_id

    def __call__(self):
        recipe = Recipe.objects.prefetch_related('ingredients__food').get(pk=self.recipe_id)
        assert recipe.auto_photo, "RecipeImageGenerator cannot be called with auto_photo == False"
        food_tags = self.select_representative_foodtags(recipe)
        if food_tags is None:
            if recipe.photo:
                recipe.photo.delete(save=True)
            return None # Failed
        # Build images from food_tags
        return self.build_image(recipe, food_tags)

    def build_image(self, recipe, food_tags):
        """
        Simple version to start with : keep only the first image
        """
        if recipe.photo:
            recipe.photo.delete(save=False)

        file_name = 'recipe_auto_' + '%.6i.jpg' % recipe.id
        if len(food_tags) == 1:
            recipe.photo.save(file_name, food_tags[0].photo.file, save=True)
            return
        # Truncating and pasting images
        images = []
        img_width = 640 / len(food_tags)
        for food_tag in food_tags:
            im = Image.open(food_tag.photo)
            if im.size[0] < img_width:
                # Picture which is not large enough
                new_height = ceil(im.size[1] * img_width / float(im.size[0]))
                im = im.resize((ceil(img_width), new_height))
            elif im.size[1] != 400:
                # Resizing the image so that the height is the standard value
                new_width = ceil(im.size[0] * 400. / float(im.size[1]))
                im = im.resize((new_width, 400))
            left  = int(im.size[0] / 2 - img_width / 2)
            right = int(im.size[0] / 2 + img_width / 2)
            im = im.crop((left, 0, right, 400))
            images.append(im)

        new_image = Image.new("RGB", (640, 400), "white")
        for i, im in enumerate(images):
            new_image.paste(im, (int(i * img_width), 0))

        # Turn back into file-like object
        image_file = io.BytesIO()
        new_image.save(image_file , 'JPEG', optimize = True)
        image_file.seek(0)    # So that the next read starts at the beginning

        recipe.photo.save(file_name, File(image_file), save=True)

    def select_representative_foodtags(self, recipe):
        """
        Select the best food tags (with images) to represent this recipe
        """
        food_tags = self.get_food_tags_from_title(recipe)
        self.fill_foodtags_from_ingredients(recipe, food_tags)

        if len(food_tags) == 0:
            return None # Failed
        return food_tags

    def get_food_tags_from_title(self, recipe):
        """
        From the title of a recipe, retrieve food_tags.
        """
        # Food tags covered by at least one ingredient of the recipe
        recipe_foodtag_ids = set()
        for ingredient in recipe.ingredients.all():
            for food_tag in ingredient.food.food_tags.all():
                recipe_foodtag_ids.add(food_tag.id)
                recipe_foodtag_ids = recipe_foodtag_ids.union(food_tag.cached_parents_ids())

        food_tags = []
        for food_tag in FoodTag.objects.all():
            if food_tag.photo and food_tag.name.lower() in recipe.name.lower():
                # Ensure that the food tags are represented by at least one of the ingredients of the recipe
                if food_tag.id in recipe_foodtag_ids:
                    food_tags.append(food_tag)
        return food_tags

    def fill_foodtags_from_ingredients(self, recipe, selected_foodtags):
        """
        From the ingredients of the recipe, return the most interesting food_tags with pictures
        """
        food_quantities = {}
        for ingredient in recipe.ingredients.all():
            food_quantities[ingredient.food] = ingredient.grams

        total_grams = sum(food_quantities.values())
        if total_grams == 0:
            return None # Failed
        ordered_ingredients = sorted(food_quantities.items(), key=lambda x: x[1], reverse=True)

        for food, quantity in ordered_ingredients:
            food_percentage = float(quantity) / total_grams
            if food_percentage < 0.05:
                # Less than 5%... this is too few to be picked up
                break
            # The ingredient is accepted either if it's the most represented, or if it represents more than 20% of ingredients
            big_enough = len(selected_foodtags) == 0 or food_percentage > 0.2
            if not big_enough:
                continue
            best_food_tag = self.select_ingredient_foodtag(food)
            if best_food_tag is None:
                continue
            if best_food_tag.id in [ft.id for ft in selected_foodtags]:
                continue
            selected_foodtags.append(best_food_tag)
            if len(selected_foodtags) == 3:
                # No more than 3 ingredients selected
                break

    def select_ingredient_foodtag(self, food=None, food_tags=None):
        # From a food, returns the best food_tag with photo
        if food_tags is None:
            food_tags = food.food_tags.all().annotate(nb_food = Count('food'))
        if len(food_tags) == 0:
            return None # Failure
        food_tags = dict((food_tag, food_tag.nb_food) for food_tag in food_tags)
        food_tags = sorted(food_tags.items(), key=lambda x: x[1])  # Ascending (food_tag, nb_food), ...
        food_tags = list(filter(lambda x: "sucre" not in x[0].name.lower() and "farine" not in x[0].name.lower(), food_tags))
        for food_tag, nb_food in food_tags:
            if food_tag.photo:
                return food_tag

        # None of the ingredient food_tags had images... try parents
        parents = []
        for food_tag, nb_food in food_tags:
            parents.extend(food_tag.parents.all().annotate(nb_food = Count('food')))
        return self.select_ingredient_foodtag(food_tags=parents)
from collections                import defaultdict

from rest_framework             import serializers, fields

from shopping_mgr.models        import ShoppingList, ShoppingItem, ShoppingCategory
from shopping_mgr.controller    import get_shopping_days, get_shopping_dish_recipes

from recipe_mgr.models          import Food, RawState, Recipe, FoodTag
from recipe_mgr.helpers         import food_conversions

from memory.controls            import MemoryManager

import datetime

class ShoppingListSerializer(serializers.ModelSerializer):
    nb_items = serializers.IntegerField(source = 'items.count', read_only = True)

    class Meta:
        model = ShoppingList
        exclude = []

class ShoppingCategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingCategory
        exclude = []

class ShoppingItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShoppingItem
        exclude = []

class ShoppingListExtendedSerializer(object):
    OTHER_CATEGORY = "Autre"

    def __init__(self, shopping_list):
        self.shopping_list = shopping_list
        if not shopping_list.user.diet:
            self.diet_exclusions = self.diet_warnings = []
        else:
            self.diet_exclusions = shopping_list.user.diet.excluded_food_tags.all().values('id', 'name')
            self.diet_warnings   = shopping_list.user.diet.forewarned_food_tags.all().values('id', 'name')
        self.all_items = list(shopping_list.items.all())
        food_ids = set(item.food_id for item in self.all_items if not item.is_custom)
        # Optimization: retrieving all foods at once (1 query only)
        foods = Food.objects.filter(pk__in = food_ids).prefetch_related('conversions', 'shopping_category', 'type')
        # Optimization: indexing data
        self.food_per_id            = dict((f.id, f) for f in foods)
        self.raw_states_per_id      = dict((r.id, r) for r in RawState.objects.all())
        self.food_dish_recipes      = self.get_food_dish_recipes()

    @classmethod
    def category_sort(cls, x):
        UNKNOWN_CATEGORY_ORDER = 1000
        category, items = x
        if category in MemoryManager.shopping_categories_order:
            return (MemoryManager.shopping_categories_order[category], 0)
        else:
            return (UNKNOWN_CATEGORY_ORDER, -sum(not item['got_it'] for item in items))

    @property
    def data(self):
        categories = defaultdict(list)
        for item in self.all_items:
            shopping_category = self.get_item_shopping_category(item)
            data = self.gen_shopping_item_data(item)
            self.check_diet_exclusions(item, data)
            categories[shopping_category].append(data)

        res = []
        for category, items in sorted(categories.items(), key=self.category_sort):
            res.append({
                'food_type': category,
                'missing_items': sum(not item['got_it'] for item in items),
                'items': sorted(items, key=lambda x: (x['got_it'], x['forced_name'] or x['food']['name'])),
            })
        return res

    def get_fly_menu_data(self):
        """
        Returns the shopping list for fly menu
        """
        res = {
            "ingredients": []
        }
        for item in self.all_items:
            if item.got_it:
                continue
            if not item.food_id:
                continue
            food = self.food_per_id[item.food_id]
            best_conversion, basic_conversion = food_conversions(food, item.grams, shopping_compatible_only=True)
            res["ingredients"].append(
                {'name': item.food.name.replace(",", ""),
                 'qty': best_conversion['value'],
                 'unit': best_conversion['unit']})
        return res

    def get_item_shopping_category(self, item):
        assert item.raw_state_id is not None or item.food_id is None, "invalid shopping item %i" % item.id
        if item.is_custom:
            return self.OTHER_CATEGORY
        raw_state = self.raw_states_per_id[item.raw_state_id]
        if raw_state.name == "en conserve":
            return "Conserves"
        elif raw_state.name == "surgelé":
            return "Surgelés"
        else:
            food = self.food_per_id[item.food_id]
            return food.shopping_category.name

    def check_diet_exclusions(self, item, data):
        if item.is_custom or (len(self.diet_exclusions) == 0 and len(self.diet_warnings) == 0):
            return

        food_tag_ids = list(MemoryManager.food_index.get_tags(item.food.id))
        for tag_type in ('diet_exclusions', 'diet_warnings'):
            tag_list = list(tag['name'] for tag in getattr(self, tag_type) if tag['id'] in food_tag_ids)
            if len(tag_list):
                data[tag_type] = tag_list

    def gen_shopping_item_data(self, item):
        if item.is_custom:
            # Custom item
            best_conversion = basic_conversion = item_recipes = freeze_date = None
            food_data = { 'id': None, 'name': item.forced_name, 'fresh_expiry': None }
        else:
            # Ingredient item
            food = self.food_per_id[item.food_id]
            fresh_expiry = None
            if self.raw_states_per_id[item.raw_state_id].name == "frais" and not food.type.usually_stored:
                fresh_expiry = food.fresh_expiry or food.type.fresh_expiry
            food_data = {'id': food.id, 'name': food.name, 'fresh_expiry': fresh_expiry}
            best_conversion, basic_conversion = food_conversions(food, item.grams, shopping_compatible_only=True)
            item_recipes = self.get_item_recipes_data(item)
            freeze_date = fresh_expiry and self.shopping_list.start_date + datetime.timedelta(fresh_expiry)
        data = {
            'food': food_data,
            'conversion': best_conversion,
            'basic_conversion': basic_conversion,
            'forced_name': item.forced_name,
            'id': item.id,
            'got_it': item.got_it,
            'forced_quantity': item.forced_quantity,
            'recipes': item_recipes,
            'freeze_date': freeze_date,
            'freeze_warning': freeze_date is not None and freeze_date <= self.shopping_list.end_date,
        }
        return data

    def get_item_recipes_data(self, item):
        if item.is_custom:
            return None
        food_dish_recipes = self.food_dish_recipes[(item.food_id, item.raw_state_id)]
        res = []
        for dish_recipe, ingredient in food_dish_recipes:
            grams = ingredient.grams_without_loss * dish_recipe.ratio
            food = self.food_per_id[item.food_id]
            best_conversion, basic_conversion = food_conversions(food, grams)
            quantity = best_conversion['value']
            if basic_conversion is not None:
                quantity = basic_conversion['value']
            res.append({
                "id":       dish_recipe.recipe.id,
                "name":     dish_recipe.recipe.name,
                "photo":    dish_recipe.recipe.photo_url,
                "date":     dish_recipe.dish.meal_slot.day.date,
                "meal":     dish_recipe.dish.meal_slot.meal_type.name,
                "quantity": quantity,
            })
        return sorted(res, key = lambda x: x["date"])

    def get_food_dish_recipes(self):
        days = get_shopping_days(self.shopping_list)
        dish_recipe_prefetch = ('recipe__ingredients__default_conversion', 'dish__meal_slot__day', 'dish__meal_slot__meal_type')
        dish_recipes = get_shopping_dish_recipes([day.id for day in days], dish_recipe_prefetch)
        food_to_dish_recipes = defaultdict(list)
        for dish_recipe in dish_recipes:
            for ingredient in dish_recipe.recipe.ingredients.all():
                food_to_dish_recipes[(ingredient.food_id, ingredient.raw_state_id)].append((dish_recipe, ingredient))
        return food_to_dish_recipes

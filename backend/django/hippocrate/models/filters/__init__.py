from hippocrate_cpp.core                    import UstensilFilter as UstensilFilterC,\
                                               ExcludeRecipeAllFilter as ExcludeRecipeAllFilterC,\
                                               ExcludeRecipeFilter as ExcludeRecipeFilterC,\
                                               TagRecipeFilter as TagRecipeFilterC,\
                                               ExcludeDataFilter as ExcludeDataFilterC,\
                                               DishTimeFilter as DishTimeFilterC,\
                                               ExcludeNonHealthyRecipesFilter as ExcludeNonHealthyRecipesFilterC
from hippocrate.controls.dish_indexing  import cpp_dish_from_dish
from hippocrate.models.recipestorage    import MainRecipeStorage

class BaseFilterPy(object):
    def description(self):
        raise NotImplementedError

    def py_accept(self, dish, recipe):
        """
        Python compliant version of Filter::accept
        Creates a CPP Dish and retrieve the RecipeData.
        @warning: the CPP Dish conversion is limited (ratios are set to a default value of 1)
        """
        cpp_dish = cpp_dish_from_dish(dish)
        recipe_data = MainRecipeStorage.get(recipe.id)
        return self.accept(cpp_dish, recipe_data)

class UstensilFilter(UstensilFilterC, BaseFilterPy):
    def __init__(self, ustensil):
        UstensilFilterC.__init__(self, ustensil.id)
        self.ustensil = ustensil

    def description(self):
        return "Ne possède pas de %s" % self.ustensil.name

class ExcludeRecipeAllFilter(ExcludeRecipeAllFilterC, BaseFilterPy):
    def __init__(self, recipe):
        ExcludeRecipeAllFilterC.__init__(self, recipe.id)
        self.recipe = recipe

    def description(self):
        return "N'aime pas %s" % self.recipe.name

class ExcludeRecipeFilter(ExcludeRecipeFilterC, BaseFilterPy):
    def __init__(self, dish, recipe):
        ExcludeRecipeFilterC.__init__(self, dish.id, recipe.id)
        self.recipe = recipe
        self.dish = dish

    def description(self):
        return "Ne souhaite pas avoir de %s" % self.recipe.name


class ExcludeNonHealthyRecipesFilter(ExcludeNonHealthyRecipesFilterC, BaseFilterPy):
    def description(self):
        return "Pas recettes perçues comme non-équilibrées"

class DishTimeFilter(DishTimeFilterC, BaseFilterPy):
    def description(self):
        return "Recettes rapides"

class TagRecipeFilter(TagRecipeFilterC, BaseFilterPy):
    def __init__(self, profile, food_tag, critical = False):
        TagRecipeFilterC.__init__(self, profile.id, food_tag.id, critical)
        self.profile = profile
        self.food_tag = food_tag

    def description(self):
        return "%s n'aime pas %s" % (self.profile.nickname, self.food_tag.name)

class ExcludeDataFilter(ExcludeDataFilterC, BaseFilterPy):

    def description(self):
        res = "Recettes avec %s" % self.data_key
        if self.min_value > 0 and self.max_value > 0:
            res += "borné(e)s"
        elif self.min_value > 0 :
            res += " minimum"
        elif self.max_value > 0 :
            res += " limité(e)s"
        return res

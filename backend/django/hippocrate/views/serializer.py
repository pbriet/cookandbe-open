from hippocrate.models.recipestorage  import MainRecipeStorage
from collections                    import defaultdict

class OldImprovementsSerializer(object):
    """
    Simple serialization of the results of an improvement with Hippocrate
    """
    @staticmethod
    def serialize(modifications):
        res = defaultdict(list)
        for dish_id, dish_modifs in modifications.items():
            for modification in dish_modifs:
                recipe_id = modification['recipe_id']
                recipe_data = MainRecipeStorage.get(recipe_id)
                res[dish_id].append({"id": recipe_id, "name": recipe_data.name})
        return res
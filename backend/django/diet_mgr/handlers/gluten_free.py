
from diet_mgr.handlers.anc      import AncStandardDiet

from recipe_mgr.models          import DishType

from planning_mgr.models        import Dish

class GlutenFreeDiet(AncStandardDiet):
    KEY = "gluten_free"
    DIAGNOSIS_ARGUMENTS = dict()

    def update_metaplanning(self, user):
        bread = DishType.get_dt(DishType.DT_BREAD)
        Dish.objects.filter(meal_slot__day__planning_id = user.meta_planning_id, dish_type_id = bread.id).delete()

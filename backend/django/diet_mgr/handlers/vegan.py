
from diet_mgr.handlers.anc              import AncStandardDiet

from recipe_mgr.models                  import DishType

from planning_mgr.models                import Dish

from hippocrate.models.constraints      import ProteinsConstraint, NutrientConstraint

class VeganDiet(AncStandardDiet):
    KEY = "vegan"
    DIAGNOSIS_ARGUMENTS = dict()
    
    def validate_constraint(self, constraint):
        if type(constraint) in (ProteinsConstraint, ):
            return None
        if type(constraint) is NutrientConstraint and constraint.key in ('vitamineb12', 'zinc', 'calcium', 'fibres'):
            return None
        return constraint

    def update_metaplanning(self, user):
        cheese = DishType.get_dt(DishType.DT_CHEESE)
        Dish.objects.filter(meal_slot__day__planning_id = user.meta_planning_id, dish_type_id = cheese.id).delete()

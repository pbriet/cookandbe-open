
from diet_mgr.handlers.anc              import AncStandardDiet

from recipe_mgr.models                  import DishType

from planning_mgr.models                import Dish

from hippocrate.models.constraints      import ProteinsConstraint

class VegetarianDiet(AncStandardDiet):
    KEY = "vegetarian"
    DIAGNOSIS_ARGUMENTS = dict()
    
    def validate_constraint(self, constraint):
        if type(constraint) in (ProteinsConstraint, ):
            return None
        return constraint

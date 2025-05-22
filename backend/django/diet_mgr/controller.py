
from django.utils               import timezone

def assign_diet(user, diet, parameters=None, default=False):
    """
    Makes the user subscribe to a diet
    @param parameters: The diet parameters : {name: value}
    """
    if parameters is None:
        parameters = {}
    diet_handler = diet.handler(user.main_profile)
    diet_handler.save_parameters(parameters)
    user.diet = diet
    if not default:
        user.diet_changed_at = timezone.now()
    diet_handler.update_metaplanning(user)
    user.meta_planning.set_modified()
    user.save()

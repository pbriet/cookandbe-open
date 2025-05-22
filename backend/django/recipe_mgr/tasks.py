
from celery import shared_task

from django.db.models           import Avg, Count

from recipe_mgr.models          import Recipe
from recipe_mgr.seasons         import SeasonManager

@shared_task
def update_seasonality():
    """
    Every day at 5am, updates the seasonality stored in the cache
    """
    SeasonManager.update_all()



@shared_task
def update_recipe_ratings():
    """
    Calculating the average ratings of all recipes
    """
    for recipe in Recipe.objects.all().annotate(calc_avg_rating=Avg('ratings__rating'),
                                                calc_nb_ratings=Count('ratings')):
        if recipe.nb_ratings != recipe.calc_nb_ratings:
            recipe.nb_ratings = recipe.calc_nb_ratings
            recipe.avg_rating = recipe.calc_avg_rating
            recipe.save()

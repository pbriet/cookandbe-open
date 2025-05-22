
from rest_framework                 import viewsets
from rest_framework.decorators      import api_view, permission_classes
from rest_framework.permissions     import AllowAny
from rest_framework.response        import Response

from common.decorators              import api_arg, api_model_arg
from common.model                   import get_field_validators
from common.permissions             import IsAdminOrReadOnlyList, Allow

from django.utils                   import timezone

from emailing                       import MessageType
from emailing.tools                 import sendmail_template

from recipe_mgr.models              import RecipeRating, Recipe
from recipe_mgr.serializers         import RecipeRatingSerializer

@api_view(['POST'])
@api_model_arg('recipe', Recipe)
@api_arg('rating', int, validators=get_field_validators(RecipeRating, 'rating'))
@api_arg('comment', str, None)
@api_arg('replace', bool, False) # If this user has already commented/rated this recipe, should we replace the existing one. Fails otherwise.
def rate_recipe(request, recipe, rating, comment, replace):
    """
    Add a rating/comment to a recipe
    """
    if recipe.author_id == request.user.id:
        return Response({"status": "error", "error": "cannot rate your own recipe"}, 400)
    existing = recipe.ratings.filter(user=request.user)
    if existing.count():
        if replace:
            existing.delete()
        else:
            return Response({"status": "error",
                             "error": "there is already a comment/rating on this recipe. Use replace=True"}, 400)

    # If there is no comment : automatically accepted. Otherwise, requires a review
    moderated_at = None
    if not comment:
        moderated_at = timezone.now()
    RecipeRating.objects.create(recipe=recipe, user=request.user, rating=rating, comment=comment, moderated_at=moderated_at)

    return Response({"status": "ok"})

@api_view(['GET'])
@api_model_arg('recipe', Recipe, allow_none=True)
def user_recipe_rating(request, recipe):
    """
    Returns the status of the recipe rating by the user
    """
    try:
        rating = RecipeRating.objects.get(user=request.user, recipe=recipe)
    except RecipeRating.DoesNotExist:
        return Response({"rated": False})
    res = {"rated": True}
    res.update(RecipeRatingSerializer(rating).data)
    return Response(res)

@api_view(['GET'])
@permission_classes((AllowAny,))
@api_model_arg('recipe', Recipe, allow_none=True)
@api_arg('moderated', bool, True)
@api_arg('offset', int, 0)
@api_arg('limit', int, 10)
def ratings_list(request, recipe, moderated, offset, limit):
    """
    List the ratings that matches the filters :
    - recipe : on a given recipe
    - moderated : only moderated ones, only non-moderated ones  (reviewer only)
    """
    is_reviewer = (not request.user.is_anonymous) and request.user.is_reviewer
    if not is_reviewer:
        if not moderated:
            return Response({"error": "only admins can retrieve non-moderated ratings"}, 403)
        if limit > 20:
            return Response({"error": "max limit is 20"}, 400)

    if recipe is None:
        ratings = RecipeRating.objects.all()
    else:
        ratings = recipe.ratings.all()
    ratings = ratings.select_related('recipe', 'user').filter(moderated_at__isnull=not moderated).order_by('-created_at')
    nb_ratings = ratings.count()
    ratings = list(ratings[offset:offset+limit])
    return Response({"data": RecipeRatingSerializer(ratings, many=True).data,
                     "nb": nb_ratings})

@api_view(['POST'])
@permission_classes((Allow("reviewer"),))
@api_model_arg('rating', RecipeRating)
@api_arg('accept', bool)
@api_arg('reason', str, None)
def moderate_rating(request, rating, accept, reason):
    """
    Accept or reject a rating/comment
    """
    if rating.moderated_at is not None:
        return Response({"error": "rating has already been moderated"}, 400)
    if accept:
        rating.moderated_at = timezone.now()
        rating.moderator = request.user
        rating.save()
    else:
        if not reason:
            return Response({"error": "'reason' is mandatory when rejecting"}, 400)
        sendmail_template(MessageType.MAIN_INFO, 'recipe_mgr/templates/rejected_rating.html', {'reason': reason,
                                                                                               'recipe': rating.recipe,
                                                                                               'comment': rating.comment},
                            'Votre commentaire nécessite des modifications', users=[rating.user],
                            tags=["recipe_reject_rating"])
        rating.delete()

    return Response({"status": "done"})
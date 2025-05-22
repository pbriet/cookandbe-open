
from django.core.exceptions     import PermissionDenied
from rest_framework             import viewsets, status
from rest_framework.decorators  import action
from rest_framework.permissions import SAFE_METHODS
from rest_framework.response    import Response
from rest_framework.views       import APIView
from collections                import defaultdict

from common.decorators          import api_arg, api_check_user_id, api_model_arg
from common.permissions         import IsOwner
from common.rest                import CustomViewSet

from eater_mgr.models           import Eater

from planning_mgr.models        import MealSlotEater, MealPlace, DishType, MealSlot

from profile_mgr.controller     import calculate_auto_time_window, set_profile_metrics, InvalidProfileValue
from profile_mgr.models         import Profile, ProfileMetric, Taste, RestrictedFood, RecipeDislike
from profile_mgr.serializers    import ProfileSerializer, TasteSerializer, RestrictedFoodSerializer, AttendanceSerializer
from profile_mgr.serializers    import ProfileMetricSerializer, RecipeDislikeSerializer, TasteWritableSerializer

from recipe_mgr.models          import RecipeTag, FoodTag, Recipe

import datetime
import json

# Maximum authorized percentage of dislike  (percentage of recipes)
MAX_DISLIKE_PERCENTAGE = 0.66

class UserProfileViewSet(viewsets.ModelViewSet):
    serializer_class = ProfileSerializer
    permission_classes = (IsOwner('creator', list = True), )

    @api_arg('user_id', int)
    @api_arg('creator', int)
    @api_check_user_id
    def create(self, request, user_id, creator, *args, **kwargs):
        """
        When creating a profile, also creating a Eater
        """
        if creator != user_id:
            raise PermissionDenied
        response = super(UserProfileViewSet, self).create(request, *args, **kwargs)
        if response.status_code == 201:
            # Creation was successful
            profile = Profile.objects.get(pk=response.data['id'])
            # Promotion to main profile if there is None
            if profile.creator.main_profile is None:
                profile.creator.main_profile = profile
                profile.creator.save()
            # By default, we create a eater that is regularly eating
            eater = Eater.objects.create(user_id = user_id, profile = profile, regular = True)
            # And we add him in every metaplanning's meals
            if profile.creator.meta_planning is not None:
                for day in profile.creator.meta_planning.days.prefetch_related('meal_slots__dishes__dish_type').all():
                    for meal_slot in day.meal_slots.all():
                        dishes = meal_slot.dishes.all()
                        if len(dishes) == 1 and dishes[0].dish_type.has_static_ratio():
                            # Don't add eaters to custom meal_slots
                            continue
                        MealSlotEater.objects.create(eater = eater, meal_slot = meal_slot)
                profile.creator.meta_planning.set_modified()
        return response

    @api_arg('user_id', int)
    @api_check_user_id
    def destroy(self, request, user_id, pk = None, **kwargs):
        profile = Profile.objects.get(pk = pk)
        if profile is not None and profile.is_main_profile:
            return Response({"error": "trying to delete main profile (id %i)" % profile.id}, 403)
        if profile.creator.meta_planning is not None:
            profile.creator.meta_planning.set_modified()
        return super().destroy(self, request, pk)

    def get_queryset(self):
        user_id = int(self.kwargs['user_id'])
        main_only = bool(self.request.query_params.get('main_only', False))
        queryset = Profile.objects.filter(creator_id = user_id).order_by("id")
        if main_only:
            queryset = queryset.filter(id = self.request.user.main_profile_id)
        return queryset

    @action(detail=True, methods=['get'])
    @api_arg('user_id', int)
    @api_check_user_id
    def nb_dislikes(self, request, user_id, pk, **kwargs):
        profile = self.get_object()
        dislikes = set()
        for taste in profile.tastes.filter(fondness__lt=0):
            dislikes.add(taste.food_tag_id)
        for restricted in profile.restrictions.all():
            dislikes.add(restricted.food_tag_id)
        return Response({"value": len(dislikes)})

    @action(detail=True, methods=['post'])
    def dislike_recipe(self, request, pk, **kwargs):
        user_id = int(kwargs['user_id'])
        if user_id != request.user.id:
            raise PermissionDenied
        params = json.loads(request.body.decode("utf-8"))
        recipe_id = int(params['recipe_id'])
        profile = self.get_object()
        RecipeDislike.objects.get_or_create(profile_id=profile.id, recipe_id=recipe_id)
        return Response({"status": "ok"}, 200)

    @action(detail=True, methods=['GET'])
    @api_check_user_id
    def get_disliked_recipes(self, request, **kwargs):
        profile_id = int(kwargs['pk'])
        query = RecipeDislike.objects.filter(profile_id = profile_id)
        return Response(RecipeDislikeSerializer(query, many = True).data, 200)

    @action(detail=True, methods=['get'])
    @api_arg('key', str)
    @api_arg('user_id', int)
    @api_arg('min_date', datetime.datetime, None)
    @api_arg('max_date', datetime.datetime, None)
    @api_arg('auto_time_window', bool, False)
    def metric_history(self, request, pk, user_id, key, min_date, max_date, auto_time_window):
        """
        Returns the history of profile values
        between some given dates
        @return: a Response containing [(date, value), (date, value), ...]
        """
        if key not in Profile.HISTORY_FIELDS:
            return Response({"error": "this metric doesn't exist"}, status=400)
        profile = self.get_object()
        if auto_time_window:
            if min_date is not None or max_date is not None:
                return Response({"error": "cannot use auto_time_window with a given min/max date"}, status=400)
            min_date, max_date = calculate_auto_time_window(profile, key)
        values = profile.history_values(key, min_date, max_date)
        return Response({"values": values,
                         "metric": ProfileMetricSerializer.serialize(ProfileMetric.objects.get(key=key))})


    @action(detail=True, methods=['post'])
    @api_arg('metrics', dict)
    @api_arg('user_id', int)
    def update_metrics(self, request, pk, user_id, metrics):
        """
        Setting a multiple metric values on a profile
        """
        profile = self.get_object()
        try:
            set_profile_metrics(profile, metrics)
        except InvalidProfileValue as e:
            return Response({"error": e.description}, status=400)
        return Response({"status": "done"})

class TasteViewSet(CustomViewSet):
    model = Taste
    exclude = []
    filtered_fields = ('profile_id',)
    permission_classes = (IsOwner('profile', 'creator', list=True), )
    LIST = True

    def get_serializer_class(self):
        # See Ugly fix in NewIngredientSerializer
        if self.request.method not in SAFE_METHODS:
            return TasteWritableSerializer
        else:
            return TasteSerializer

    @api_arg('profile', int)
    @api_arg('food_tag', int)
    @api_arg('set_planning_expired', bool)
    def create(self, request, profile, food_tag, set_planning_expired):
        """
        Create a new taste for this user.
        Ensure that no more than 25% of recipes are disliked
        """
        if Taste.objects.filter(profile_id=profile, food_tag_id=food_tag).count() > 0:
            return Response({"status": "already disliked"}, 200)

        nb_total_recipes = Recipe.objects.filter(status=Recipe.STATUS_PUBLISHED, internal=False).count()
        tag_to_recipes = FoodTag.cached_recipes()

        disliked_recipes = set()
        food_tag_ids = [ft.id for ft in FoodTag.objects.filter(tastes__profile__creator=request.user).only('id')]

        food_tag_ids.append(food_tag)

        for tag_id in food_tag_ids:
            disliked_recipes = disliked_recipes.union(tag_to_recipes.get(tag_id, []))

        if len(disliked_recipes) / nb_total_recipes > MAX_DISLIKE_PERCENTAGE:
            return Response({"status": "too_many_disliked"}, 200)

        if set_planning_expired:
            request.user.meta_planning.set_modified()

        return super().create(request)


    def destroy(self, request, *args, **kargs):
        request.user.meta_planning.set_modified()
        return super().destroy(request, *args, **kargs)

class RestrictedFoodViewSet(viewsets.ModelViewSet):
    queryset = RestrictedFood.objects.all()
    serializer_class = RestrictedFoodSerializer
    permission_classes = (IsOwner('profile', 'creator', list=True), )

class AttendanceView(APIView):
    def get_profile_attendances(self, meta_planning, profile, is_main_profile):
        # Temporary dictionnary {day_index : {meal_type : attendance}} used to initialise the profile's attendances
        not_eating   = MealPlace.objects.get(key = "donoteat")
        attendances  = defaultdict(dict)
        days = meta_planning.sorted_days
        assert len(days) <= 7, "cannot use attendance with more than 7 days"
        for day in days:
            for meal_slot in day.ordered_meal_slots:
                attendance = not_eating
                if profile in [eater.profile for eater in meal_slot.eaters.all()] and \
                (is_main_profile or meal_slot.meal_place.key == "home"):
                    attendance = meal_slot.meal_place
                attendances[day.weekday][meal_slot.meal_type] = attendance
        return attendances

    def get(self, request, **kargs):
        profile     = Profile.objects.get(pk = self.kwargs['profile_id'])
        if profile.creator != self.request.user:
            raise PermissionDenied
        attendances = self.get_profile_attendances(profile.creator.meta_planning, profile, self.request.user.main_profile == profile)
        res         = AttendanceSerializer.serialize(attendances)
        return Response(res)

    def set_profile_attendances(self, meta_planning, profile, attendances):
        meta_week_days = meta_planning.sorted_days
        profile_eater = Eater.objects.get(user=meta_planning.user, profile=profile)
        assert len(meta_week_days) <= 7, "cannot use attendance with more than 7 days"
        for week_day, meal_data in attendances.items():
            for meal_type, meal_place in meal_data.items():
                meal_slot = MealSlot.objects.get(day=meta_week_days[week_day], meal_type = meal_type)
                if meal_slot.meal_place == meal_place:
                    continue
                meal_slot.meal_place = meal_place
                meal_slot.save()
                meal_slot.meal_slot_eaters.all().delete()
                if meal_place.key != "home":
                    # Switching to external place, or 'donoteat' : only main profile eats
                    MealSlotEater.objects.create(eater=profile_eater, meal_slot=meal_slot)
                else:
                    # Switching to home : every body eats
                    for eater in meta_planning.user.eaters.all():
                        MealSlotEater.objects.create(eater=eater, meal_slot=meal_slot)

    def put(self, request, **kargs):
        if int(self.kwargs['profile_id']) != self.request.user.main_profile.id:
            raise PermissionDenied
        if len(request.data) == 0:
            return Response({"error": "no data provided"}, 400)
        profile = Profile.objects.get(pk = self.kwargs['profile_id'])
        self.set_profile_attendances(self.request.user.meta_planning, profile, AttendanceSerializer.deserialize(request.data))
        if self.request.user.meta_planning is not None:
            self.request.user.meta_planning.set_modified()
        return Response(request.data)

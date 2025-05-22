
from collections                import defaultdict
from django.core.exceptions     import PermissionDenied

from eater_mgr.models           import Eater

from planning_mgr.models        import MetaPlanning, MealSlotEater, MealPlace
from planning_mgr.serializers   import HomeAttendanceSerializer

from rest_framework.response    import Response
from rest_framework.views       import APIView


class HomeAttendanceView(APIView):
    # Attendance dictionnary {day_index : {meal_type : {eater : attendance}}}

    def get_home_attendances(self, planning):
        not_eating   = MealPlace.objects.get(key = "donoteat")
        eaters       = planning.user.eaters.all()
        attendances  = defaultdict(dict)
        main_eater   = planning.user.eaters.get(profile = planning.user.main_profile)
        for day in sorted(planning.days.all(), key=lambda x: x.date):
            for meal_slot in day.ordered_meal_slots:
                # Cas des repas hors du foyer
                if meal_slot.meal_place.key != "home" or (not meal_slot.suggest):
                    # attendances[day.weekday][meal_slot.meal_type] = {main_eater : meal_slot.meal_place}
                    attendances[day.weekday][meal_slot.meal_type] = dict()
                    continue
                non_main_eaters = [eater for eater in eaters if eater.id != main_eater.id]
                # Cas des repas en commun
                attendances[day.weekday][meal_slot.meal_type] = dict((eater, not_eating) for eater in non_main_eaters)
                for eater in meal_slot.eaters.all():
                    if meal_slot.meal_place.key == "home":
                        attendances[day.weekday][meal_slot.meal_type][eater] = meal_slot.meal_place
        return attendances

    def get(self, request, **kargs):
        planning    = MetaPlanning.objects.get(pk = self.kwargs['planning_id'])
        if planning.user != self.request.user:
            raise PermissionDenied
        attendances = self.get_home_attendances(planning)
        res         = HomeAttendanceSerializer.serialize(planning, attendances)
        return Response(res)

    def set_home_attendances(self, user, days, attendances):
        print("set_home_attendances")
        main_profile_eater = Eater.objects.get(profile_id=user.main_profile_id, user_id=user.id)
        days = sorted(days, key=lambda x: x.date)
        for week_day, day_data in attendances.items():
            day = days[week_day]
            for meal_slot in day.meal_slots.all():
                meal_data = day_data[meal_slot.meal_type]
                meal_slot.meal_slot_eaters.all().delete()
                # Adding main_eater, always present to any meal
                MealSlotEater.objects.create(meal_slot=meal_slot, eater=main_profile_eater)
                if meal_slot.meal_place.key == "donoteat":
                    # No eater
                    continue
                if meal_slot.meal_place.key == "home":
                    # Given eaters
                    for eater, meal_place in meal_data.items():
                        if meal_place.key == "home":
                            if eater.id != main_profile_eater.id:
                                MealSlotEater.objects.create(meal_slot = meal_slot, eater = eater)

    def put(self, request, **kargs):
        if request.user.meta_planning_id is None or int(self.kwargs['planning_id']) != request.user.meta_planning_id:
            raise PermissionDenied
        if len(request.data) == 0:
            return Response({"error": "no data provided"}, 400)
        days = request.user.meta_planning.days.all().prefetch_related('meal_slots__meal_slot_eaters',
                                                                      'meal_slots__meal_place',
                                                                      'meal_slots__meal_type')
        self.set_home_attendances(self.request.user, days, HomeAttendanceSerializer.deserialize(request.user.meta_planning, request.data))
        request.user.meta_planning.set_modified()
        return Response(request.data)

from rest_framework             import viewsets

from common.permissions         import IsOwner
from planning_mgr.models        import Dish, MealPlace
from planning_mgr.serializers   import DishSerializer, MealPlaceSerializer


class MealPlaceViewSet(viewsets.ModelViewSet):
    queryset = MealPlace.objects.all()
    serializer_class = MealPlaceSerializer

class DishViewSet(viewsets.ModelViewSet):
    queryset = Dish.objects.all()
    serializer_class = DishSerializer
    permission_classes = (IsOwner('meal_slot', 'day', 'user'), )

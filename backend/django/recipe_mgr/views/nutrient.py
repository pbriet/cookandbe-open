
from rest_framework             import viewsets
from rest_framework.decorators  import api_view
from rest_framework.response    import Response

from common.nutrients           import NUTRIENT_CATEGORIES
from common.permissions         import IsAdminOrReadOnlyList

from nutrient.models            import Nutrient
from nutrient.serializers       import NutrientSerializer

@api_view(['GET'])
def nutrient_categories(self):
    """
    Returns the nutrient categories
    """
    return Response(NUTRIENT_CATEGORIES, 200)

class NutrientViewSet(viewsets.ModelViewSet):
    """
    This viewset automatically provides `list`, `create`, `retrieve`,
    `update` and `destroy` actions.
    """
    serializer_class = NutrientSerializer
    permission_classes = (IsAdminOrReadOnlyList, )

    def get_queryset(self):
        return Nutrient.objects.filter(enabled=True)

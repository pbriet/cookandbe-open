from rest_framework             import viewsets

from common.permissions         import IsAdminOrReadOnlyList

from recipe_mgr.models          import Ustensil, UstensilCategory
                                       
from recipe_mgr.serializers     import UstensilSerializer, UstensilCategorySerializer
                                   
class UstensilCategoryViewSet(viewsets.ModelViewSet):
    queryset = UstensilCategory.objects.all()
    serializer_class = UstensilCategorySerializer
    permission_classes = (IsAdminOrReadOnlyList, )

class UstensilViewSet(viewsets.ModelViewSet):
    queryset = Ustensil.objects.all()
    serializer_class = UstensilSerializer
    permission_classes = (IsAdminOrReadOnlyList, )


from django.db.models           import Count

from rest_framework             import viewsets
from rest_framework.decorators  import api_view
from rest_framework.response    import Response

from common.decorators          import api_arg, api_model_arg
from common.permissions         import IsAdminOrReadOnlyList

from recipe_mgr.helpers         import detect_aggregations
from recipe_mgr.models          import DishType
from recipe_mgr.serializers     import DishTypeSerializer

import copy


class DishTypeViewSet(viewsets.ReadOnlyModelViewSet):
    serializer_class = DishTypeSerializer
    permission_classes = (IsAdminOrReadOnlyList, )

    @api_arg('exclude_unions', bool, None)
    def get_queryset(self, exclude_unions):
        queryset = DishType.objects.order_by('name')
        if exclude_unions is None or not exclude_unions:
            return queryset.all()
        # We return only Dishtypes which are not "master" of a dish type unions
        return queryset.annotate(nb_unions_as_master=Count('unions_as_master')).filter(nb_unions_as_master=0)

@api_view(['GET'])
@api_model_arg('dish_types', DishType, is_list=True)
def find_dish_type_aggregations(request, dish_types):
    """
    Given a list of dish type ids, return the possible variants (aggregations)
    @rtype: a list of list of dish type ids
    """
    dish_type_ids = [dt.id for dt in dish_types]
    res = [dish_type_ids]

    for master_dish_type_id, sub_dish_type_ids in detect_aggregations(dish_type_ids).items():
        variant = copy.copy(dish_type_ids)
        # Replacing the sub_dish_types by the master dish type in the variant
        for sub_dish_type_id in sub_dish_type_ids:
            i = variant.index(sub_dish_type_id)
            del variant[i]
        variant.insert(i, master_dish_type_id)
        res.append(variant)
    return Response(res, 200)


from rest_framework.decorators  import api_view, permission_classes
from rest_framework.response    import Response

import copy

from common.decorators          import api_arg, api_model_arg, api_check_user_id
from common.permissions         import Allow

from nutrient.models            import CookingMethodEffect, Nutrient, NutrientPack
from nutrient.serializers       import CookingMethodEffectSerializer, NutrientPackSerializer

from recipe_mgr.models          import FoodType, CookingMethod

from optalim.config             import Config


@api_view(['GET'])
@permission_classes([Allow('operator')])
@api_model_arg("food_type", FoodType)
def cooking_method_effects(request, food_type):
    """
    Returns the list of cooking method effects on a food
    """
    effects = CookingMethodEffect.objects.filter(food_type=food_type).order_by('cooking_method__id')
    data = CookingMethodEffectSerializer(effects, many=True).data
    return Response({"data": data}, 200)

@api_view(['POST'])
@permission_classes([Allow('operator')])
@api_model_arg("food_type", FoodType)
@api_model_arg("cooking_method", CookingMethod)
@api_arg("weight_ratio", float)
def set_cooking_method_effect(request, food_type, cooking_method, weight_ratio):
    """
    Modifies the effect of one cooking method on one food
    """
    try:
        effect = CookingMethodEffect.objects.get(food_type=food_type, cooking_method=cooking_method)
    except CookingMethodEffect.DoesNotExist:
        CookingMethodEffect.objects.create(food_type=food_type, cooking_method=cooking_method, weight_ratio=weight_ratio)
    else:
        effect.weight_ratio = weight_ratio
        effect.save()
    return Response({"status": "ok"}, 201)


@api_view(['GET'])
@api_check_user_id
def api_get_nutrient_packs(request, user_id):
    """
    Returns the list of nutrients, and if there are enabled or not
    """
    all_packs = NutrientPack.objects.all().order_by('order')

    user_packs = request.user.nutrient_packs.all()
    user_pack_ids = [up.id for up in user_packs]

    res = []
    for pack in all_packs:

        serialized = NutrientPackSerializer(pack).data

        # Transforming list of nutrients in dictionnary  key => nutrient
        serialized['nutrients'] = dict((nut['key'], nut) for nut in serialized['nutrients'])

        serialized['enabled'] = pack.id in user_pack_ids

        res.append(serialized)

    return Response({"data": res}, 200)


@api_view(['POST'])
@api_check_user_id
@api_arg('pack_key', str)
@api_arg('enable', bool)
def api_enable_nutrient_pack(request, user_id, pack_key, enable):
    """
    Enable or disable a nutrient pack for a given user
    """
    user_packs = request.user.nutrient_packs.all()
    user_pack_by_key = dict((up.key, up) for up in user_packs)

    if pack_key in user_pack_by_key:
        if not enable:
            request.user.nutrient_packs.remove(user_pack_by_key[pack_key])
    else:
        if enable:
            pack = NutrientPack.objects.get(key=pack_key)
            request.user.nutrient_packs.add(pack)

    request.user.meta_planning.set_modified()

    return Response({"status": "ok"}, 201)
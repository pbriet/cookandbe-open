from common.math                import round_to_closest

from optalim.config             import Config

from recipe_mgr.models          import DishType

from collections                import defaultdict, OrderedDict

from math                       import sqrt, log, pow
import copy
import time

def detect_aggregations(dish_type_ids, master_dish_type_object=False):
    """
    From a list of dish_type_ids, returns the aggregations detected inside
    @rtype: {dish_type_aggregated_id: [dish_type_ids]}
    @param master_dish_type_object: if True, returns {dish_type_aggregated_object: [dish_type_ids]}
    """
    res = OrderedDict()
    for master_dish_type in DishType.objects.filter(aggregations_as_master__id__gt=0).order_by('id'):
        agg_ids = set()
        for sub_dishtype_id in master_dish_type.sub_dishtype_ids:
            agg_ids.add(sub_dishtype_id)
        if agg_ids.issubset(dish_type_ids):
            if master_dish_type_object:
                res[master_dish_type] = agg_ids
            else:
                res[master_dish_type.id] = agg_ids
    return res

def food_conversions(food, grams, default_conversion=None, use_only_default=False, shopping_compatible_only=False):
    """
    Given some ingredient, and an amout of grams, returns the list of conversions
    sorted from the best to the worst one.
    Also give the "basic conversion" (grams, ml, ...)
    
    # For each conversion :
    # - its name
    # - its value (rounded)
    # - what is the ratio comparing to default conversion
    # - how much information is lost (in %)
    # - the score of this conversion
    """
    if default_conversion:
        assert default_conversion.food_id == food.id, "conversion is not a conversion for this food !"
    if use_only_default:
        conversions = [default_conversion]
    else:
        conversions = list(food.conversions.all())
        if shopping_compatible_only:
            conversions = [cv for cv in conversions if cv.shopping_compatible]
    
    options = []
    for conversion in conversions:
        data = evaluate_conversion(conversion, grams, default_conversion)
        options.append((conversion, data))
    
    options = sorted(options, key=lambda x: x[1]['score'])
    
    best_conversion, best_conversion_data = options[0]
    best_conversion_data['html_value'] = html_quantity_value(best_conversion_data['value'])
    
    if best_conversion_data['basic']:
        # The best conversion is a basic one already
        return best_conversion_data, None
    
    basic_options = [opt[1] for opt in options if opt[1]['basic']]

    if len(basic_options) > 1:
        # There are other basic options than 'gramme' -> removing it
        basic_options = [opt for opt in basic_options if 'g' == opt['unit']]
    if len(basic_options):
        basic_option = basic_options[0] # The most correct conversion
        # Applying the loss of the best conversion, so that it is taken into account in the equivalency
        basic_option['value'] /= float(1 - best_conversion.loss_coeff)
        basic_option['value'] = clever_grams_round(basic_option['value'])
        basic_option['html_value'] = html_quantity_value(basic_option['value'])
        if basic_option['value'] < 10:
            basic_option = None # Don't display basic value if it's too small
    else:
        basic_option = None
        
    return best_conversion_data, basic_option

def clever_grams_round(value, splittable=False):
    
    # lost_data is how much information we lose by doing this conversion
    # An rounding it to the closest integer
    if value < 5:
        if not splittable:
            # Must be an integer
            closest = max(1, round(value))
        else:
            if value > 1 and value < 5 :
                # Between 1 and 5, we allow halfs (x.5)
                closest = round_to_closest(value, 0.5)
            elif value <= 1:
                # Under 1, we allow quarters  (x.25, x.75)
                closest = round_to_closest(value, 0.25)
                # And thirds (x.33, x.67)
                closest_third = round_to_closest(value, 0.333333)
                if abs(value - closest) > abs(value - closest_third):
                    closest = closest_third
    elif value > 1000:
        # Over 1000, we round to the closest hundred
        closest = round_to_closest(value, 100)
    elif value > 100:
        # Over 100, we round to the closest ten
        closest = round_to_closest(value, 10)
    elif value > 30:
        # Over 30, we round to the closest 5
        closest = round_to_closest(value, 5)
    else:
        closest = round(value)
    
    if int(closest) == closest:
        closest = int(closest)
    
    return closest

def evaluate_conversion(conversion, grams, default_conversion=None):
    """
    Retrieve infos about a conversion, and calculates its score of "diplayability"
    @param conversion: the FoodConversion object
    @param grams: the quantity (in grams)
    """
    is_basic = conversion.unit in ('g', 'ml')
        
    # Applying the loss due to this conversion  (default stored values for grams is relative to default_conversion)
    default_loss_coeff = default_conversion.loss_coeff if default_conversion else 0
    loss_coeff_comparing_to_default = (1 - conversion.loss_coeff) / (1 - default_loss_coeff)
    
    option_value = grams / (conversion.value * loss_coeff_comparing_to_default)
    
    # lost_data is how much information we lose by doing this conversion
    # An rounding it to the closest integer
    closest = clever_grams_round(option_value, conversion.splittable)

    if option_value > 0.0:
        lost_data = abs(closest - option_value) / option_value
    else:
        lost_data = 0.0
        closest = 0.0

    res = {'value': round(closest, 2),
           'loss':  round(100 * lost_data, 2)}
    
    if closest > 1:
        res['unit'] = conversion.unit_plural
    else:
        res['unit'] = conversion.unit
    
    res['value'] = round(closest, 2)
    res['loss'] = round(100 * lost_data, 2)

    # Calculation of score :
    # * We want to avoid loss of data due to rounding values
    # * We want to minimize the value if over 1

    number_penalty = 0
    if closest >= 1:
        # Avoiding too big numbers
        number_penalty += log(closest)/10

    non_integer = abs(round(closest) - closest)
    if non_integer == 0.5:
        # Halfs : not encouraging
        number_penalty += 0.1
    elif non_integer > 0.1:
        # Quarters and thirds : penalizing more
        number_penalty += 0.3

    lost_data_penalty = float((lost_data * 100)**3) / 2000
    
    # When quantities are low (< 50g), loss is less a concern
    lost_data_penalty *= 1 + min(0, (min(50, grams)  - 50.)/50)
    
    grams_penalty = 0
    if is_basic:
        grams_penalty = 0.3
        number_penalty /= 2 # High numbers are expected with basic conversions
    
    # The more the pow coefficient is high, the less the data loss is a priority
    res['score'] = round(lost_data_penalty + number_penalty + grams_penalty, 2)
    
    res['id'] = conversion.id
    res['basic'] = conversion.unit.split(' ')[0] in ('g', 'ml', 'l', 'kg')
    res['grams'] = grams

    return res

def html_quantity_value(value):
    """
    From a quantity, return the HTML code to display it
    """
    if value == 0.25:
        return "&frac14;"
    if value == 0.33:
       return "1/3" # &frac13 is only defined in HTML 5
    if value == 0.5:
       return "&frac12;"
    if value == 0.67:
       return "2/3" # &frac23 is only defined in HTML 5
    if value == 0.75:
       return "&frac34;"
    if value == 1.5:
       return "1 et &frac12;"
    return str(value)
from paybox         import Level

from math           import ceil

from common.date    import today_aware
from paybox.models  import GlobalSpecialOffer

from collections    import defaultdict


##  This file contains the current prices

# Dimension 1 : level
# Dimension 2 : number of months
# Prices in euros (cents)
BASE_PRICES = {
    Level.PREMIUM : {
        1:  1500,
        3:  1200,
        12: 1000
    },
    # Level.PREMIUM    : {
    #     1:  2000,
    #     3:  1500,
    #     12: 1000
    # }
}

def get_discount_per_level():
    """
    Return current discounts for each level
    """
    current_special_offers = GlobalSpecialOffer.objects.filter(start_date__lte=today_aware(),
                                                               end_date__gte=today_aware())
    discount_per_level = defaultdict(int)
    for offer in current_special_offers:
        if offer.level is None:
            discounted_levels = (Level.PREMIUM,) #Level.FREEDOM,
        else:
            discounted_levels = (offer.level,)
        for level in discounted_levels:
            discount_per_level[level] = max(discount_per_level[level], offer.discount)
    return discount_per_level

def get_prices_and_discount(min_discount=0, cents_to_euros=False):
    """
    Returns a dictionary like :
    {level.FREEDOM:
        1: {'monthly_cost': 4000, 'discount': 50, 'after_discount': 2000}
    """
    discount_per_level = get_discount_per_level()

    res = {}
    for level, prices in BASE_PRICES.items():
        discount = max(min_discount, discount_per_level[level])
        level_tariffs = {}
        res[level] = level_tariffs
        for nb_months, cents in prices.items():
            final_cost = cents * (1 - float(discount) / 100)
            final_cost = ceil(final_cost)
            if cents_to_euros:
                cents = round(float(cents) / 100, 2)
                final_cost = round(float(final_cost) / 100, 2)
            level_tariffs[nb_months] = {'monthly_cost': cents,
                                        'discount': discount,
                                        'after_discount': final_cost}
    return res


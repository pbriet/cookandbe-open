from collections                import defaultdict
from recipe_mgr.models          import FoodTag

from optalim.log import logger

def store_food_tag_parent_ids(food_tag, food_tags_dict, result_set, initial_food_tag=None):
    """
    Recursively returns the parent food tag ids of a given food tag
    @param food_tags_dict: a dictionnary of all food tags (id -> food_tag)
    @param result_set: set containing all the parent ids
    @param initial_food_tag: the first food tag that started the recursive call, to detect a cycle
    """
    if initial_food_tag is None:
        initial_food_tag = food_tag
    for parent in food_tag.parents.all():
        if parent.id == initial_food_tag.id:
            assert False, "Cycle detected in food tags : %s <-> %s" % (parent.name, food_tag.name)
        result_set.add(parent.id)
        result_set = store_food_tag_parent_ids(food_tags_dict[parent.id], food_tags_dict, result_set, initial_food_tag)
    return result_set

def cache_food_tags():
    """
    Load food tags from the database, and stores the list of food ids associated to each food tag
    (including children with hierarchy)
    """
    food_tags = list(FoodTag.objects.prefetch_related('parents').all())
    food_tags_dict = dict((ft.id, ft) for ft in food_tags)

    needs_update = False

    for food_tag in food_tags:
        if food_tag.cached_parents_ids(none_if_not_existing=True) is None:
            needs_update = True

    # Storing in cache
    if needs_update:
        logger.info("Updating cache with %i food tags" % len(food_tags))

        for food_tag in food_tags:
            parent_ids = set()
            store_food_tag_parent_ids(food_tag, food_tags_dict, parent_ids)
            food_tag.cache_parents_ids(parent_ids)

    return needs_update

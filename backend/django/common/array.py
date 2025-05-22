"""
Helpers functions
"""
from operator import attrgetter

def sortBy(objs, attribute_name, reverse=False):
    return sorted(objs, key=attrgetter(attribute_name), reverse=reverse)
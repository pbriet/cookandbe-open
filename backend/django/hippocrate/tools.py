import numpy

def random_pick(l):
    """
    Returns a random element in a list
    """
    return l[numpy.random.random_integers(0, len(l) - 1)]

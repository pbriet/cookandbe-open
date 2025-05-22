
from django.core.cache.backends.dummy   import DummyCache as DjangoDummyCache

class DummyCache(DjangoDummyCache):
    """
    Default cache used for tests, does nothing.
    Overrides django dummy class to add some specific Redis methods
    """
    def keys(*args, **kargs):
        return set()
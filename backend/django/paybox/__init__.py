
class Level(object):
    MIN           = 0

    FREE          = 0  # No subscription for this level (default one)
    # FREEDOM       = 1
    PREMIUM       = 1

    MAX           = 1


LEVEL_NAMES = {
    Level.FREE:     'free',
    # Level.FREEDOM:  'freedom',
    Level.PREMIUM:  'premium'
}


LEVEL_PUBLIC_NAMES = {
    Level.FREE:     'Gratuit',
    # Level.FREEDOM:  'Liberté',
    Level.PREMIUM:  'Premium'
}
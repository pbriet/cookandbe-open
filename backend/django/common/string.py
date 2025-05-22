import unicodedata


def unaccent(value):
    """
    Remove accents from string
    """
    return unicodedata.normalize('NFKD', value.lower().strip()).encode('ASCII', 'ignore').decode("utf-8")
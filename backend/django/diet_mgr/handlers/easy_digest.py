from diet_mgr.handlers.anc      import AncStandardDiet

class EasyDigestDiet(AncStandardDiet):
    """
    Diet that helps to have a better digestion
    """
    KEY = "easy_digest"
    DIAGNOSIS_ARGUMENTS = dict()
    
    NUTRIENT_FAST_AMEND = {
        'lipids': {'min': 30, 'max': 35, 'cost': 100}, # High priority
    }


from diet_mgr.handlers.cardiovascular   import CardiovascularDietHandler

class NormolipidicDietHandler(CardiovascularDietHandler):
    """
    Normolipidic diet preventing cholesterol issues
    """
    KEY = "normolipidic"
    DIAGNOSIS_ARGUMENTS = dict()
    
    def _diagnose(self, arguments):
        arguments['normolipidic']   = 1
        arguments['hypertension']   = 0
        arguments['diabete']        = 0
        arguments['anticoagul']     = 0
        return super()._diagnose(arguments)

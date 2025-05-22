
from diet_mgr.handlers.cardiovascular   import CardiovascularDietHandler

class HypertensionDietHandler(CardiovascularDietHandler):
    """
    Normolipidic diet preventing cholesterol issues
    """
    KEY = "hypertension"
    DIAGNOSIS_ARGUMENTS = dict()
    
    def _diagnose(self, arguments):
        arguments['normolipidic']   = 0
        arguments['hypertension']   = 1
        arguments['diabete']        = 0
        arguments['anticoagul']     = 0
        return super()._diagnose(arguments)

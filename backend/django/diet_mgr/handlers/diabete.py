
from diet_mgr.handlers.cardiovascular   import CardiovascularDietHandler

class DiabeteDietHandler(CardiovascularDietHandler):
    """
    Diabete diet controlling tryglicerids
    """
    KEY = "diabete"
    DIAGNOSIS_ARGUMENTS = dict()
    
    def _diagnose(self, arguments):
        arguments['normolipidic']   = 0
        arguments['hypertension']   = 0
        arguments['diabete']        = 1
        arguments['anticoagul']     = 0
        return super()._diagnose(arguments)

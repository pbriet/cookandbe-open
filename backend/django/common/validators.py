
from django.core.exceptions import ValidationError

def ValueInValidator(accepted_values):
    def fcn(value):
        if value not in accepted_values:
            raise ValidationError("La valeur doit être parmi %s (valeur : %s)" % (accepted_values, value))
    return fcn
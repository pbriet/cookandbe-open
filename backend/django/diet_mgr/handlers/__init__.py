
class InvalidDietParametersException(Exception):
    """
    Raised when subscribing a diet with invalid parameters
    """
    pass

class MissingDietParameter(InvalidDietParametersException):
    def __init__(self, missing_parameter):
        self.missing_parameter = missing_parameter
    def __str__(self):
        return "Paramètre manquant : %s" % self.missing_parameter

class InvalidDietParameterType(InvalidDietParametersException):
    def __init__(self, invalid_type):
        self.invalid_type = invalid_type
    def __str__(self):
        return "Type invalide pour le paramètre : %s" % self.invalid_type

class UnknownDietParameter(InvalidDietParametersException):
    def __init__(self, unknown_parameter):
        self.unknown_parameter = unknown_parameter
    def __str__(self):
        return "Paramètre inattendu : %s" % self.unknown_parameter

class NonValidatedDietParametersException(InvalidDietParametersException):
    def __init__(self, message):
        self.message = message
    def __str__(self):
        return self.message

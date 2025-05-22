
import numpy

def pearson_correlation(left_array, right_array):
    return numpy.corrcoef(left_array, right_array)[0, 1]

def round_to_closest(value, modulo):
    """
    round to the closest value so that :
    <closest value> % module == 0

    e.g. : round_to_closest(94, 10) -> 90
           round_to_closest(1.6, 0.5) -> 1.5
    """
    res = round(float(value) / float(modulo)) * modulo
    if int(modulo) == modulo:
        return int(res)
    return res


def round_to_closest_ratio(value, modulo):
    """
    Round to closest, with a minimum value of minimum ratio
    """
    res = round_to_closest(value, modulo)
    if res < 0.5:
        return 0.5
    return res
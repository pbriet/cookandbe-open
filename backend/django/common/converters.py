import json
import datetime

from common.date                import parse_date_str, parse_datetime_str

def parse_dict(value):
    """
    """
    if type(value) is dict: return value
    return json.loads(value)

def convert_bool(value):
    if type(value) is not str:
        return bool(value)
    value = value.lower()
    if value in ("true", "1"):
        return True
    if value in ("false", "0"):
        return False
    raise ValueError("Invalid value for expected type boolean")

def convert_float(value):
    if type(value) is not str:
        return float(value)
    return float(value.replace(",", "."))

# Converters that raise ValueError in case of failure, and
# returns the converted value
TYPE_CONVERTERS = {
    int: lambda x: int(x),
    float: convert_float,
    datetime.date: parse_date_str,
    datetime.datetime: parse_datetime_str,
    bool: convert_bool,
    str: lambda x: x,
    dict: parse_dict
 }

def convert(value, expected_type):
    return TYPE_CONVERTERS[expected_type](value)

def can_convert(expected_type):
    return expected_type in TYPE_CONVERTERS
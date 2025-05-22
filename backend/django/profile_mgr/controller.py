from django.utils               import timezone

from common.converters          import convert

from profile_mgr.models         import Profile

import datetime
import numpy

class InvalidProfileValue(Exception):
    """
    Something wrong happened when setting a profile value
    """
    def __init__(self, description):
        super().__init__()
        self.description = description
    
    def __str__(self):
        return self.description

def calculate_auto_time_window(profile, key):
    """
    On a profile with a given metric key, calculate what is a nice min/max date to display
    ~ max 5 values, quite regular
    """
    
    # No more than 2 month ago
    min_date = timezone.now().date() - datetime.timedelta(days=60)
    
    values = profile.history_values(key, min_date)
    if len(values) == 0:
        return timezone.now(), None
    
    # No more than 5 values
    if len(values) > 5:
        values = values[-5:]
    
    # There shouldn't be more than 2*stddev, or less than stddev/2, between two X values
    x_values = [v[0].timestamp() for v in values]
    
    min_date = values[-1][0]
    
    for i in range(1, len(values)):
        std_val = numpy.std(x_values[-i - 1:])
        if x_values[-i] - x_values[-i - 1] > std_val * 2:
            break # The gap is too big - stopping here
        if x_values[-i] - x_values[-i - 1] < std_val / 2:
            break # The gap is too small - stopping here
        min_date = values[-i - 1][0]
    
    return min_date - datetime.timedelta(seconds=60), None


def set_profile_metrics(profile, metrics):
    """
    Given a profile, set values like weight, height, with a given dictionnary
    """
    for key, value in metrics.items():
        try :
            key = convert(key, str)
            value = convert(value, float)
        except ValueError:
            raise InvalidProfileValue("invalid types")
        if key not in Profile.HISTORY_FIELDS:
            raise InvalidProfileValue("this metric doesn't exist")
        setattr(profile, key, value)
    profile.save()
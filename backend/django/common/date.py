from datetime                   import time, timedelta, datetime, date
from django.utils               import timezone
from django.core.exceptions     import ValidationError
from django.conf                import settings

import calendar

def is_aware(dt):
    return bool(dt.tzinfo)

def today():
    """
    Very simple function, it only makes it easier to mock
    """
    return date.today()

def today_aware():
    return date_to_datetime(today())

def tz_datetime(*args):
    return datetime(*args, tzinfo=timezone.get_default_timezone())

def date_to_datetime(d, time=None):
    """
    converts a date into a datetime
    """
    if time is None:
        time = datetime.min.time()
    return tz_aware(datetime.combine(d, time))

def valid_future(date):
    """
    raise a ValidationError if the date seems to be really in the past (and shouldn't)
    WARNING: we set a 2 days error margin, due to timezones and locations
    """
    if date <= today() - timedelta(days = 2):
        raise ValidationError("date is in the past")

def get_current_week(user = None, skip_weeks = 0):
    """
    Returns an interval of 2 dates representing the current week:

    @param skip_weeks: give the X following week  (1 <> not current week, but next)
    """
    today = timezone.now().date()

    if user is None:
        # Caculating 1st day of next week
        first_day_next_week = today + timedelta(days = 7 * skip_weeks - today.weekday())
    else:
        day_shift = (today.weekday() - user.shopping_day) % 7
        first_day_next_week = today + timedelta(days = 7 * skip_weeks - day_shift)

    # Calculating last day of next week
    last_day_next_week = first_day_next_week + timedelta(days=6)

    return first_day_next_week, last_day_next_week

def get_next_week(user = None, skip_weeks = 0):
    """
    Returns an interval of 2 dates containing next week

    @param skip_weeks: give the X following week  (1 <> not next week, but the following)
    """
    return get_current_week(user, skip_weeks = 1 + skip_weeks)

def tz_aware(date_time):
    """
    Transforms a datetime into a datetime timezone-aware (using server timezone)
    """
    if date_time.tzinfo is not None and date_time.tzinfo.utcoffset(date_time) is not None:
        return date_time
    return timezone.make_aware(date_time, timezone.get_default_timezone())

def make_utc(date_time):
    """
    Transforms a datetime as being UTC
    """
    dt = timezone.make_aware(date_time, timezone.utc)
    assert is_aware(dt)
    return dt

def parse_date_str(value, pattern=None):
    if isinstance(value, date):
        return value
    if pattern is None:
        pattern = "%Y-%m-%d"
    return tz_aware(datetime.strptime(value, pattern)).date()

def parse_datetime_str(str_date):
    if str_date[-1] != 'Z':
        # Locate ":" in string
        _seps = [i for i, c in enumerate(str_date) if c == ':']
        # Expected 3 separators : H:M:S and 02:00 (timezone)
        assert len(_seps) == 3, "Cannot parse date str %s" % str_date
        # Removing ":" from timezone to be compatible with strptime
        str_date = str_date[:_seps[2]] + str_date[_seps[2]+1:]
        try:
            return datetime.strptime(str_date, '%Y-%m-%dT%H:%M:%S.%f%z')
        except ValueError:
            return datetime.strptime(str_date, '%Y-%m-%dT%H:%M:%S%z')

    try:
        return make_utc(datetime.strptime(str_date[:-1], '%Y-%m-%dT%H:%M:%S.%f'))
    except ValueError:
        return make_utc(datetime.strptime(str_date[:-1], '%Y-%m-%dT%H:%M:%S'))

    # return make_utc(datetime.strptime(str_date[:19].replace('T', ' '), "%Y-%m-%d %H:%M:%S"))

def timeAdd(start_time, hours = 0, minutes = 0, seconds = 0):
    # OMG, python can't add time to a datetime.time on its own...
    delta = timedelta(seconds = start_time.second + 60 * start_time.minute + 3600 * start_time.hour)
    delta += timedelta(seconds = seconds + 60 * minutes + 3600 * hours)
    return time(hour = delta.seconds // 3600, minute = (delta.seconds % 3600) // 60, second = delta.seconds % 60)

def add_days(date, nb=1):
    return date + timedelta(days=nb)

def get_tomorrow():
    return add_days(today(), 1)

def get_yesterday():
    return add_days(today(), -1)

def get_one_week_ago():
    return add_days(today(), -7)

def seconds_from_midnight():
    now_val = timezone.now()
    return now_val.hour * 3600 + now_val.minute * 60 + now_val.second

def get_month_range(specific_date=None, tzinfo=None):
    if specific_date is None:
        specific_date = today()
    first_day_index, last_day_number = calendar.monthrange(specific_date.year, specific_date.month)
    start = date(specific_date.year, specific_date.month, 1)
    end = date(specific_date.year, specific_date.month, last_day_number)
    if tzinfo is not None:
        start = timezone.make_aware(datetime.combine(start, datetime.min.time()), tzinfo)
        end = timezone.make_aware(datetime.combine(end, datetime.max.time()), tzinfo)
    return start, end

def add_months(sourcedate, months):
    month = sourcedate.month - 1 + months
    year = sourcedate.year + month // 12
    month = month % 12 + 1
    day = min(sourcedate.day, calendar.monthrange(year, month)[1])
    return date(year, month, day)
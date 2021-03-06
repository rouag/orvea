# -*- coding: utf-8 -*-
import math
from datetime import datetime


def time_float_convert(time_val):
    time_val = str(time_val)
    vals = time_val.split(':')
    val = int(vals[0]) * 60.0 * 60.0 + int(vals[1]) * 60.0 + int(vals[2])
    return val / 3600.0


def float_time_convert(float_val):
    factor = float_val < 0 and -1 or 1
    val = abs(float_val)
    return (factor * int(math.floor(val)), int(round((val % 1) * 60)))


def float_time_convert_str(float_val):
    factor = float_val < 0 and -1 or 1
    val = abs(float_val)
    hour = factor * int(math.floor(val))
    minute = int(round((val % 1) * 60))
    return '%s:%s' % (str(hour).zfill(2), str(minute).zfill(2))


def days_between(d1, d2):
    d1 = datetime.strptime(d1, "%Y-%m-%d")
    d2 = datetime.strptime(d2, "%Y-%m-%d")
    return abs((d2 - d1).days + 1)

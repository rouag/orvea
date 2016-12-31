# -*- coding: utf-8 -*-
import math


def time_float_convert(time_val):
    time_val = str(time_val)
    vals = time_val.split(':')
    print vals
    val = int(vals[0]) * 60.0 * 60.0 + int(vals[1]) * 60.0 + int(vals[2])
    return val / 3600.0


def float_time_convert(float_val):
    factor = float_val < 0 and -1 or 1
    val = abs(float_val)
    return (factor * int(math.floor(val)), int(round((val % 1) * 60)))

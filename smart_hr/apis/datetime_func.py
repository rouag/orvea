# -*- coding: utf-8 -*-

from datetime import datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT
from umalqurra.hijri_date import HijriDate

# Date range generator
def daterange(start_date, end_date):
    for n in range(int((end_date - start_date).days) + 1):
        yield start_date + timedelta(n)

# Converter from Float to Time
def convert_float_to_time(val):
    ft_str = str(val).split('.')
    g_time = ('%02d' % int(ft_str[0])) + ':' + ('%02d' % int(float('0.' + ft_str[1]) * 60)) + ':00'
    return g_time

"""
    This function used for calculating execution time for some functions
"""
def timespent(seconds):
    intervals = (
        ('weeks', 604800),
        ('days', 86400),
        ('hours', 3600),
        ('minutes', 60),
        ('seconds', 1),
    )
    # Variables
    ret = ''
    for name, count in intervals:
        value = seconds // count
        if value:
            seconds -= value * count
            ret += ' ' + str(value) + ' ' + name
    return ret

"""
    The purpose of this function is to convert
    total seconds to actual time in
    (seconds, minutes, hours, days, weeks).
"""
def elapsed_time(secs):
    intervals = (
        # ('weeks', 126000), # 5 Days per Week
        ('days', 25200), # 7 Hours per Day
        ('hours', 3600),
        ('minutes', 60),
        ('seconds', 1),
    )
    # Variables
    seconds = 0
    minutes = 0
    hours = 0
    days = 0
    weeks = 0
    for name, count in intervals:
        value = secs // count
        if value:
            secs -= value * count
            if name == 'seconds':
                seconds = value
            elif name == 'minutes':
                minutes = value
            elif name == 'hours':
                hours = value
            elif name == 'days':
                days = value
            elif name == 'weeks':
                weeks = value
    return (seconds, minutes, hours, days, weeks)

# Get Start & End date of the Hijri year
def get_start_end_hijri_date(date_gr):
    rec_date = datetime.strptime(date_gr, DEFAULT_SERVER_DATE_FORMAT)
    date_start = HijriDate(rec_date.year, rec_date.month, rec_date.day, gr=True)
    date_start.set_date(date_start.year, 1, 1)
    date_end = date_start
    date_start = datetime(int(date_start.year_gr), int(date_start.month_gr), int(date_start.day_gr)).strftime(DEFAULT_SERVER_DATE_FORMAT)
    date_end.set_date(date_end.year + 1, 1, 1)
    date_end = datetime(int(date_end.year_gr), int(date_end.month_gr), int(date_end.day_gr)) - timedelta(days=1)
    date_end = HijriDate(date_end.year, date_end.month, date_end.day, gr=True)
    date_end = datetime(int(date_end.year_gr), int(date_end.month_gr), int(date_end.day_gr)).strftime(DEFAULT_SERVER_DATE_FORMAT)
    return date_start, date_end
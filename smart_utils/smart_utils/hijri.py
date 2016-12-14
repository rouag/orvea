# -*- coding: utf-8 -*-

from umalqurra.hijri_date import HijriDate
from umalqurra.hijri import Umalqurra
from datetime import date, timedelta

def next_date(initial_date, years=0, months=0, days=0):
    """
    Increment/decrement hijri dates using hijri values
    :param initial_date: date
    :param years: int
    :param months: int
    :param days: int
    :return: date
    """
    hijri_date = HijriDate(initial_date.year, initial_date.month, initial_date.day, gr=True)
    um = Umalqurra()
    year_gr, month_gr, day_gr = um.hijri_to_gregorian(hijri_date.year+years, hijri_date.month+months, hijri_date.day+days)
    return date(int(year_gr), int(month_gr), int(day_gr))

def current_hijri_month():
    '''
     calculates the current hijri month georgian interval
     :return: [biginig_date end_date ]
    '''
    current_gr = date.today()
    current_hijri = HijriDate(current_gr.year, current_gr.month, current_gr.day, gr=True)
    um = Umalqurra()
    first_day_gr =  um.hijri_to_gregorian(current_hijri.year, current_hijri.month, 1)
    #last day +1
    last_day_gr = um.hijri_to_gregorian(current_hijri.year, current_hijri.month +1 , 1)
    return date(int(first_day_gr[0]), int(first_day_gr[1]), int(first_day_gr[2])) , date(int(last_day_gr[0]), int(last_day_gr[1]), int(last_day_gr[2])) - timedelta(days=-1)

def current_hijri_year():
    '''
     calculates the current hijri year georgian interval
     :return [biginig_date end_date ]
    '''
    current_gr = date.today()
    current_hijri = HijriDate(current_gr.year, current_gr.month, current_gr.day, gr=True)
    um = Umalqurra()
    first_day_gr =  um.hijri_to_gregorian(current_hijri.year, 1, 1)
    #last day +1
    last_day_gr = um.hijri_to_gregorian(current_hijri.year+1, 1 , 1)
    return date(int(first_day_gr[0]), int(first_day_gr[1]), int(first_day_gr[2])) , date(int(last_day_gr[0]), int(last_day_gr[1]), int(last_day_gr[2])) - timedelta(days=-1)

def get_hijri_month_name(date):
    if date:
        hijri_date = HijriDate(date.year, date.month, date.day, gr=True)
        return hijri_date.month_name
    return None

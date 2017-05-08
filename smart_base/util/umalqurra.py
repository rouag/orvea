# -*- coding: utf-8 -*-

from datetime import date, timedelta

# for month use
MONTHS = {1: 'محرّم',
          2: 'صفر',
          3: 'ربيع الأول',
          4: 'ربيع الثاني',
          5: 'جمادي الأولى',
          6: 'جمادي الآخرة',
          7: 'رجب',
          8: 'شعبان',
          9: 'رمضان',
          10: 'شوال',
          11: 'ذو القعدة',
          12: 'ذو الحجة'}
DAYS = {1: 30,
        2: 29,
        3: 30,
        4: 30,
        5: 30,
        6: 29,
        7: 29,
        8: 30,
        9: 29,
        10: 29,
        11: 30,
        12: 29}


def get_current_month_hijri(HijriDate):
    um = HijriDate.today()
    return str(int(um.month)).zfill(2)


def get_hijri_month_start(HijriDate, Umalqurra, month):
    if month:
        um = HijriDate.today()
        um.set_date(um.year, month, 1)
        umalqurra = Umalqurra()
        start_date = umalqurra.hijri_to_gregorian(um.year, um.month, um.day)
        return date(int(start_date[0]), int(start_date[1]), int(start_date[2]))


def get_hijri_month_end(HijriDate, Umalqurra, month):
    if month:
        um = HijriDate.today()
        um.set_date(um.year, month, DAYS[month])
        umalqurra = Umalqurra()
        end_date = umalqurra.hijri_to_gregorian(um.year, um.month, um.day)
        return date(int(end_date[0]), int(end_date[1]), int(end_date[2]))


def get_hijri_month_start_by_year(HijriDate, Umalqurra, year, month):
    if month:
        um = HijriDate.today()
        um.set_date(year, month, 1)
        umalqurra = Umalqurra()
        start_date = umalqurra.hijri_to_gregorian(um.year, um.month, um.day)
        return date(int(start_date[0]), int(start_date[1]), int(start_date[2]))


def get_hijri_month_end__by_year(HijriDate, Umalqurra, year, month):
    if month:
        um = HijriDate.today()
        um.set_date(year, month, DAYS[month])
        umalqurra = Umalqurra()
        end_date = umalqurra.hijri_to_gregorian(um.year, um.month, um.day)
        return date(int(end_date[0]), int(end_date[1]), int(end_date[2]))


def get_hijri_year_by_date(HijriDate, Umalqurra, date):
    """
    @param: date: georgian date
    @return: hijri year
    """
    if date:
        hijri_date = HijriDate(date.year, date.month, date.day, gr=True)
        return int(str(int(hijri_date.year)).zfill(2))


def get_hijri_month_by_date(HijriDate, Umalqurra, date):
    """
    @param: date: georgian date
    @return: hijri month
    """
    if date:
        hijri_date = HijriDate(date.year, date.month, date.day, gr=True)
        return int(str(int(hijri_date.month)).zfill(2))


def get_hijri_date(date, separator):
    '''
    convert georging date to hijri date
    :return hijri date as a string value
    '''
    if date:
        hijri_date = HijriDate(date.year, date.month, date.day, gr=True)
        return str(int(hijri_date.day)).zfill(2) + separator + str(int(hijri_date.month)).zfill(2) + separator + str(int(hijri_date.year))
    return None


# def current_hijri_year():
#     '''
#      calculates the current hijri year georgian interval
#      :return [biginig_date end_date ]
#     '''
#     current_gr = date.today()
#     current_hijri = HijriDate(current_gr.year, current_gr.month, current_gr.day, gr=True)
#     um = Umalqurra()
#     first_day_gr = um.hijri_to_gregorian(current_hijri.year, 1, 1)
#     # last day +1
#     last_day_gr = um.hijri_to_gregorian(current_hijri.year + 1, 1 , 1)
#     return date(int(first_day_gr[0]), int(first_day_gr[1]), int(first_day_gr[2])), date(int(last_day_gr[0]), int(last_day_gr[1]), int(last_day_gr[2])) - timedelta(days=-1)
# print "hello"
# print current_hijri_year()
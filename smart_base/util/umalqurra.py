# -*- coding: utf-8 -*-

from datetime import date, timedelta

# for month use
MONTHS = [('01', 'محرّم'),
          ('02', 'صفر'),
          ('03', 'ربيع الأول'),
          ('04', 'ربيع الثاني'),
          ('05', 'جمادي الأولى'),
          ('06', 'جمادي الآخرة'),
          ('07', 'رجب'),
          ('08', 'شعبان'),
          ('09', 'رمضان'),
          ('10', 'شوال'),
          ('11', 'ذو القعدة'),
          ('12', 'ذو الحجة')]
DAYS = {'01': 30,
        '02': 29,
        '03': 30,
        '04': 30,
        '05': 30,
        '06': 29,
        '07': 29,
        '08': 30,
        '09': 29,
        '10': 29,
        '11': 30,
        '12': 29}


def get_current_month_hijri(HijriDate):
    um = HijriDate.today()
    return str(int(um.month)).zfill(2)

def get_hijri_month_start(HijriDate, Umalqurra, month):
    if month:
        um = HijriDate.today()
        um.set_date(um.year, int(month), 1)
        umalqurra = Umalqurra()
        start_date = umalqurra.hijri_to_gregorian(um.year, um.month, um.day)
        return date(int(start_date[0]), int(start_date[1]), int(start_date[2]))

def get_hijri_month_end(HijriDate, Umalqurra, month):
    if month:
        um = HijriDate.today()
        um.set_date(um.year, int(month), DAYS[month])
        umalqurra = Umalqurra()
        end_date = umalqurra.hijri_to_gregorian(um.year, um.month, um.day)
        return date(int(end_date[0]), int(end_date[1]), int(end_date[2]))


def get_hijri_date(date, separator):
    '''
    convert georging date to hijri date
    :return hijri date as a string value
    '''
    if date:
        hijri_date = HijriDate(date.year, date.month, date.day, gr=True)
        return str(int(hijri_date.year)) + separator + str(int(hijri_date.month)) + separator + str(int(hijri_date.day))
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
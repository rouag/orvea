# -*- coding: utf-8 -*-

from umalqurra.hijri_date import HijriDate

# for month use
# MONTHS = [('01', 'محرّم'),
#           ('02', 'صفر'),
#           ('03', 'ربيع الأول'),
#           ('04', 'ربيع الثاني'),
#           ('05', 'جمادي الأولى'),
#           ('06', 'جمادي الآخرة'),
#           ('07', 'رجب'),
#           ('08', 'شعبان'),
#           ('09', 'رمضان'),
#           ('10', 'شوال'),
#           ('11', 'ذو القعدة'),
#           ('12', 'ذو الحجة')]


def get_current_month_hijri():
    um = HijriDate.today()
    return str(int(um.month)).zfill(2)

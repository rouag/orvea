# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from datetime import date, datetime, timedelta



def _compute_duration(self, date_from, date_to):
        if date_from and date_to:
            date_from = fields.Date.from_string(date_from)
            date_to = fields.Date.from_string(date_to)
            daygenerator = (date_from + timedelta(x + 1) for x in xrange((date_to - date_from).days))
            sum_minus_weekends = sum(1 for day in daygenerator if day.weekday() not in [4,5])
            self.duration= sum_minus_weekends
            hr_public_holiday_obj = self.env['hr.public.holiday']
            holidays_intersections_days = 0
            for public_holiday in hr_public_holiday_obj.search(['|','&',('state', '=', 'done'),'&',('date_from', '<=',date_to),('date_to', '>=',date_to)
                                                            ,'&',('state', '=', 'done'),'&',('date_to', '>=',date_from),('date_to', '<=',date_to)
                                                            ]):
                public_holiday_date_from = fields.Date.from_string(public_holiday.date_from)
                public_holiday_date_to = fields.Date.from_string(public_holiday.date_to)
                holidays_intersections_days += self.compute_intersion_days(date_from , date_to, public_holiday_date_from, public_holiday_date_to)
        self.duration -= holidays_intersections_days


def compute_intersion_days(self,date_from1,date_to1,date_from2, date_to2):
        if date_from1 >= date_from2 and date_to2 >= date_to1:
            daygenerator = (date_from1 + timedelta(x + 1) for x in xrange((date_to1 - date_from1).days))
            duration = sum(1 for day in daygenerator if day.weekday() not in [4,5])
        if date_from2 >= date_from1 and date_to2 <= date_to1:
            daygenerator = (date_from2 + timedelta(x + 1) for x in xrange((date_to2 - date_from2).days))
            duration = sum(1 for day in daygenerator if day.weekday() not in [4,5])
        if date_from2 >= date_from1 and date_to2 >= date_to1:
            duration = (date_to1 - date_from2).days
            daygenerator = (date_to1 + timedelta(x + 1) for x in xrange((date_to1 - date_from2).days))
            duration = sum(1 for day in daygenerator if day.weekday() not in [4,5])            
        return duration
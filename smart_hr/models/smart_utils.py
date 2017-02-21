# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from datetime import date, datetime, timedelta
import datetime as dt

class SmartUtils(models.Model):

    _name = 'hr.smart.utils'

    def compute_duration(self, date_from, date_to):
        if date_from and date_to:
            if not isinstance(date_from, dt.date):
                date_from = fields.Date.from_string(date_from)
            if not isinstance(date_to, dt.date):
                date_to = fields.Date.from_string(date_to)
            duration = self.compute_days_minus_weekends(date_from, date_to)
            duration -= self.compute_holidays_days(date_from, date_to)
            return duration

    def compute_days_minus_weekends(self, date_from, date_to):
        dayDelta = timedelta(days=1)
        diff = 0
        while date_from <= date_to:
            if date_from.weekday() not in [4,5]:
                diff += 1
            date_from += dayDelta
        return diff

    def compute_holidays_days(self, date_from, date_to):
        hr_public_holiday_obj = self.env['hr.public.holiday']
        holidays_intersections_days = 0
        duration = 0
        for public_holiday in hr_public_holiday_obj.search(['|', '&', ('state', '=', 'done'), '&', ('date_from', '<=', date_to), ('date_to', '>=', date_to)
                                                                , '&', ('state', '=', 'done'), '&', ('date_to', '>=', date_from), ('date_to', '<=', date_to)]):
            public_holiday_date_from = fields.Date.from_string(public_holiday.date_from)
            public_holiday_date_to = fields.Date.from_string(public_holiday.date_to)
            if date_from >= public_holiday_date_from and public_holiday_date_to >= date_from:
                duration += self.compute_days_minus_weekends(date_from, public_holiday_date_to)
            if public_holiday_date_from >= date_from and public_holiday_date_to <= date_to:
                duration += self.compute_days_minus_weekends(public_holiday_date_from, public_holiday_date_to)
            if public_holiday_date_from >= date_from and public_holiday_date_to >= date_to:
                duration += self.compute_days_minus_weekends(public_holiday_date_from, date_to)
        return duration

    def check_holiday_day(self, date):
        hr_public_holiday_obj = self.env['hr.public.holiday']
        holidays = hr_public_holiday_obj.search([('state', '=', 'done'), ('date_from', '<=', date), ('date_to', '>=', date)])
        if holidays:
            return True
        else:
            return False

    def compute_date_to(self, date_from, duration):
        if date_from and duration:
            date_from = fields.Date.from_string(date_from)
            new_date_to = date_from
            while duration > 0:
                is_holiday= self.check_holiday_day(new_date_to)
                weekday =  new_date_to.weekday()
                new_date_to += timedelta(days=1)
                if weekday  in [4, 5] or is_holiday is True:
                    continue
                duration -= 1
            while new_date_to.weekday() in [4, 5] or self.check_holiday_day(new_date_to) is True:
                new_date_to += timedelta(days=1)
            return new_date_to

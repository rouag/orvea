# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from datetime import date, datetime, timedelta
import datetime as dt


class SmartUtils(models.Model):
    _name = 'hr.smart.utils'

    def compute_duration_deputation(self, date_from, date_to, deputation_id):
        '''
        @return: return duration betwwen two dates without public holidays, weekends,
                 and all holidays execpt for sicknes holidays
        '''
        if date_from and date_to:
            if not isinstance(date_from, dt.date):
                date_from = fields.Date.from_string(date_from)
            if not isinstance(date_to, dt.date):
                date_to = fields.Date.from_string(date_to)
            duration = self.minus_days_deputation(date_from, date_to, deputation_id)
            return duration

    def minus_days_deputation(self, date_from, date_to, deputation_id):
        dayDelta = timedelta(days=1)
        diff = 0
        employee_id = deputation_id.employee_id
        holidays_ids = set()
        print date_from, date_to 
        while date_from <= date_to:
            diff += 1
            hol_domain = [('date_from', '>=', date_from),
                          ('date_to', '<=', date_from),
                          ('state', '=', 'done'),
                          ('compute_as_deputation', '=', False),
                          ('holiday_status_id', '=', self.env.ref('smart_hr.data_hr_holiday_status_illness').id)]
            if employee_id:
                hol_domain.append(('employee_id', '=', employee_id.id))
            if date_from.weekday() not in [4, 5]:
                diff -= 1
            # check if looped date is correspanding to none compelling holiday
            holiday_id = self.env['hr.holidays'].search(hol_domain)
            if holiday_id:
                holidays_ids.add(holiday_id)
                diff -= 1
            date_from += dayDelta
        for rec in holidays_ids:
            diff += rec.deputation_balance_computed
        # minus 3ids
        diff -= self.compute_holidays_days(date_from, date_to)
        if diff > 0:
            return diff
        else:
            return 0

    def compute_duration_overtime(self, date_from, date_to, overtime_id):
        '''
        @return: return duration betwwen two dates without public holidays, weekends,
                 deputations and all holidays execpt for compelling ones
        '''
        if date_from and date_to:
            if not isinstance(date_from, dt.date):
                date_from = fields.Date.from_string(date_from)
            if not isinstance(date_to, dt.date):
                date_to = fields.Date.from_string(date_to)
            duration = self.minus_days_overtime(date_from, date_to, overtime_id)
            return duration

    def minus_days_overtime(self, date_from, date_to, overtime_id):
        dayDelta = timedelta(days=1)
        diff = 0
        employee_id = overtime_id.employee_id
        type = overtime_id.type
        # case 1: normal_days
        if type == 'normal_days':
            while date_from <= date_to:
                dep_domain = [('date_from', '>=', date_from),
                              ('date_to', '<=', date_from),
                              ('state', '=', 'done')]
                hol_domain = [('date_from', '>=', date_from),
                              ('date_to', '<=', date_from),
                              ('state', '=', 'done'),
                              ('holiday_status_id', '!=', self.env.ref('smart_hr.data_hr_holiday_status_compelling').id)]
                if employee_id:
                    dep_domain.append(('employee_id', '=', employee_id.id))
                    hol_domain.append(('employee_id', '=', employee_id.id))
                if date_from.weekday() not in [4, 5]:
                    diff += 1
                # check if looped date is correspanding to a deputation
                deputation_id = self.env['hr.deputation'].search(dep_domain)
                # check if looped date is correspanding to none compelling holiday
                holiday_id = self.env['hr.holidays'].search(hol_domain)
                if holiday_id:
                    diff -= 1
                if deputation_id:
                    diff -= 1
                date_from += dayDelta
            # minus 3ids
            diff -= self.compute_holidays_days(date_from, date_to)
        # case 2: friday_saturday
        if type == 'friday_saturday':
            while date_from <= date_to:
                dep_domain = [('date_from', '>=', date_from),
                              ('date_to', '<=', date_from),
                              ('state', '=', 'done')]
                hol_domain = [('date_from', '>=', date_from),
                              ('date_to', '<=', date_from),
                              ('state', '=', 'done'),
                              ('holiday_status_id', '!=', self.env.ref('smart_hr.data_hr_holiday_status_compelling').id)]
                if employee_id:
                    dep_domain.append(('employee_id', '=', employee_id.id))
                    hol_domain.append(('employee_id', '=', employee_id.id))
                if date_from.weekday() in [4, 5]:
                    diff += 1
                    # check if looped date is correspanding to a deputation
                    deputation_id = self.env['hr.deputation'].search(dep_domain)
                    # check if looped date is correspanding to none compelling holiday
                    holiday_id = self.env['hr.holidays'].search(hol_domain)
                    if holiday_id:
                        diff -= 1
                    if deputation_id:
                        diff -= 1
                date_from += dayDelta
        # case 3: 3ids
        if type == 'holidays':
            hr_public_holiday_obj = self.env['hr.public.holiday']
            hr_public_holiday_ids = hr_public_holiday_obj.search(['|', '&', ('state', '=', 'done'), '&', ('date_from', '<=', date_to),
                                                                  ('date_to', '>=', date_to),
                                                                  '&', ('state', '=', 'done'),
                                                                  '&', ('date_to', '>=', date_from),
                                                                  ('date_to', '<=', date_to)])
            diff = 0
            for public_holiday in hr_public_holiday_ids:
                public_holiday_date_from = fields.Date.from_string(public_holiday.date_from)
                public_holiday_date_to = fields.Date.from_string(public_holiday.date_to)
                if date_from >= public_holiday_date_from and public_holiday_date_to >= date_from:
                    date_from = date_from
                    date_to = public_holiday_date_to
                if public_holiday_date_from >= date_from and public_holiday_date_to <= date_to:
                    date_from = public_holiday_date_from
                    date_to = public_holiday_date_to
                if public_holiday_date_from >= date_from and public_holiday_date_to >= date_to:
                    date_from = public_holiday_date_from
                    date_to = date_to
                while date_from <= date_to:
                    diff += 1
                    dep_domain = [('date_from', '>=', date_from),
                                  ('date_to', '<=', date_from),
                                  ('state', '=', 'done')]
                    hol_domain = [('date_from', '>=', date_from),
                                  ('date_to', '<=', date_from),
                                  ('state', '=', 'done'),
                                  ('holiday_status_id', '!=', self.env.ref('smart_hr.data_hr_holiday_status_compelling').id)]
                    if employee_id:
                        dep_domain.append(('employee_id', '=', employee_id.id))
                        hol_domain.append(('employee_id', '=', employee_id.id))
                    # check if looped date is correspanding to a deputation
                    deputation_id = self.env['hr.deputation'].search(dep_domain)
                    # check if looped date is correspanding to none compelling holiday
                    holiday_id = self.env['hr.holidays'].search(hol_domain)
                    if holiday_id:
                        diff -= 1
                    if deputation_id:
                        diff -= 1
                    date_from += dayDelta
        if diff > 0:
            return diff
        else:
            return 0

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
            if date_from.weekday() not in [4, 5]:
                diff += 1
            date_from += dayDelta
        return diff

    def compute_holidays_days(self, date_from, date_to):
        hr_public_holiday_obj = self.env['hr.public.holiday']
        holidays_intersections_days = 0
        duration = 0
        for public_holiday in hr_public_holiday_obj.search(
                ['|', '&', ('state', '=', 'done'), '&', ('date_from', '<=', date_to), ('date_to', '>=', date_to)
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
        holidays = hr_public_holiday_obj.search(
            [('state', '=', 'done'), ('date_from', '<=', date), ('date_to', '>=', date)])
        if holidays:
            return True
        else:
            return False

    def compute_date_to(self, date_from, duration):
        if date_from and duration:
            date_from = fields.Date.from_string(date_from)
            new_date_to = date_from
            while duration > 0:
                is_holiday = self.check_holiday_day(new_date_to)
                weekday = new_date_to.weekday()
                new_date_to += timedelta(days=1)
                if weekday in [4, 5] or is_holiday is True:
                    continue
                duration -= 1
            while new_date_to.weekday() in [4, 5] or self.check_holiday_day(new_date_to) is True:
                new_date_to += timedelta(days=1)
            return new_date_to

# check if date is in official holiday, weekend or employee in holiday
    def check_holiday_weekend_days(self, date, employee_id):
        if date:
            if not isinstance(date, dt.date):
                date = fields.Date.from_string(date)
            if self.check_holiday_day(date):
                return "official holiday"
            elif date.weekday() in [4, 5]:
                return "weekend"
            elif self.env['hr.holidays'].search_count([('state', '=', 'done'), ('date_from', '<=', date), ('date_to', '>=', date), ('employee_id', '=', employee_id.id)]) != 0:
                return "holiday"
            else:
                return False

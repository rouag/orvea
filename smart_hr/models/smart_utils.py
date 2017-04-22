# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from datetime import date, datetime, timedelta
import datetime as dt
from openerp.addons.smart_base.util.time_util import days_between


class SmartUtils(models.Model):
    _name = 'hr.smart.utils'

    def get_overlapped_periode(self, date_from, date_to, operation_date_from, operation_date_to):
        """
        @return: overlapped peiode, date_fbegin, date_end
        """

        def intersection_date_set(d1, d2):
            delta = d2 - d1
            return set([d1 + timedelta(days=i) for i in range(delta.days + 1)])

        range1 = [date_from, date_to]
        range2 = [operation_date_from, operation_date_to]
        listset = intersection_date_set(*range1) & intersection_date_set(*range2)
        if listset:
            listset = sorted(listset)
            return listset[0], listset[-1]
        else:
            return False, False

    def get_overlapped_days(self, date_from, date_to, ranges):
        """
        @param: ranges array of arrays. each one have date_from, date_to
        @return: overlapped days bettwen periode and other periodes
        """

        def intersection_date_set(d1, d2):
            delta = d2 - d1
            return set([d1 + timedelta(days=i) for i in range(delta.days + 1)])

        days = 0
        range1 = [date_from, date_to]
        for range2 in ranges:
            listset = intersection_date_set(*range1) & intersection_date_set(*range2)
            if listset:
                days += len(listset)
        return days

    def compute_duration_difference(self, employee_id, date_from, date_to, normal_day, weekend, holidays):
        days = 0
        dayDelta = timedelta(days=1)
        res = []
        mydict = {}
        if date_from and date_to:
            if not isinstance(date_from, dt.date):
                date_from = fields.Date.from_string(date_from)
            if not isinstance(date_to, dt.date):
                date_to = fields.Date.from_string(date_to)
            grid_id_start, basic_salary_start = employee_id.get_salary_grid_id(date_from)
            grid_id_end, basic_salary_end = employee_id.get_salary_grid_id(date_to)
            if grid_id_start and grid_id_end and grid_id_start == grid_id_end:
                grid_id = grid_id_start
                basic_salary = basic_salary_start
                mydict = {'date_from': date_from, 'date_to': date_to, 'days': days, 'grid_id': grid_id, 'basic_salary': basic_salary}
            # case 1: same salary grid_id for all periode
            if mydict:
                while date_from <= date_to:
                    # minus normal days
                    if not normal_day and date_from.weekday() not in [4, 5]:
                        days -= 1
                    # minus vendredi et samedi
                    if not weekend and date_from.weekday() in [4, 5]:
                        days -= 1
                    # minus jours fiérie
                    if not holidays:
                        hol_domain = [('date_from', '<=', date_from),
                                      ('date_to', '>=', date_from),
                                      ('state', '=', 'done')
                                      ]
                        holiday_id = self.env['hr.public.holiday'].search(hol_domain, limit=1)
                        if holiday_id:
                            days -= 1
                    date_from += dayDelta
                    days += 1
                if days < 0:
                    days = 0
                # if days is correspending to a full month than we must return 30
                if days == 29:
                    days = 30.0
                mydict['days'] = days
                res.append(mydict)
            # case 2: different salary grid_ids for all periode
            if not mydict:
                grid_id, basic_salary = employee_id.get_salary_grid_id(date_from)
                date_start = date_from
                while date_from <= date_to:
                    days += 1
                    # minus normal days
                    if not normal_day and date_from.weekday() not in [4, 5]:
                        days -= 1
                    # minus vendredi et samedi
                    if not weekend and date_from.weekday() in [4, 5]:
                        days -= 1
                    # minus jours fiérie
                    if not holidays:
                        hol_domain = [('date_from', '<=', date_from),
                                      ('date_to', '>=', date_from),
                                      ('state', '=', 'done')
                                      ]
                        holiday_id = self.env['hr.public.holiday'].search(hol_domain, limit=1)
                        if holiday_id:
                            days -= 1
                    current_grid_id, basic_salary_temp = employee_id.get_salary_grid_id(date_from)
                    if grid_id and current_grid_id and grid_id != current_grid_id:
                        # append old value of my_dict
                        if days:
                            mydict = {'date_from': date_start, 'date_to': date_from, 'days': days, 'grid_id': grid_id, 'basic_salary': basic_salary}
                            res.append(mydict)
                            date_start = date_from + dayDelta
                            grid_id = current_grid_id
                            basic_salary = basic_salary_temp
                            days = 0
                    if grid_id and current_grid_id and grid_id == current_grid_id and date_from == date_to:
                        # update laste dict
                        if days:
                            mydict = {'date_from': date_start, 'date_to': date_to, 'days': days, 'grid_id': current_grid_id, 'basic_salary': basic_salary_temp}
                            res.append(mydict)
                    # add one day
                    date_from += dayDelta
        return res

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
                              ('date_to', '>=', date_from),
                              ('state', '=', 'done')]
                hol_domain = [('date_from', '>=', date_from),
                              ('date_to', '>=', date_from),
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
                              ('date_to', '>=', date_from),
                              ('state', '=', 'done')]
                hol_domain = [('date_from', '>=', date_from),
                              ('date_to', '>=', date_from),
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
            # TODO: check this domain
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
                                  ('date_to', '>=', date_from),
                                  ('state', '=', 'done')]
                    hol_domain = [('date_from', '>=', date_from),
                                  ('date_to', '>=', date_from),
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

    def public_holiday_intersection(self, date):
        if not isinstance(date, dt.date):
            date = fields.Date.from_string(date)

        hr_public_holiday_obj = self.env['hr.public.holiday']
        inter = hr_public_holiday_obj.search([('state', '=', 'done'), ('date_from', '<=', date), ('date_to', '>=', date)], limit=1)
        if inter:
            date_from = fields.Date.from_string(inter.date_from)
            inter_count = (date - date_from).days + 1
            return inter_count


# -*- coding: utf-8 -*-

from openerp import models, api, fields, _
from openerp.exceptions import ValidationError
from openerp.addons.smart_base.util.time_util import days_between


class hrDifference(models.Model):
    _inherit = 'hr.difference'

    @api.multi
    def get_difference_overtime(self):
        line_ids = []
        overtime_line_obj = self.env['hr.overtime.ligne']
        grid_detail_allowance_obj = self.env['salary.grid.detail.allowance']
        # 1- overtime
        overtime_setting = self.env['hr.overtime.setting'].search([], limit=1)
        # over time start in this month end finish in this month or after
        overtime_lines1 = overtime_line_obj.search([('date_from', '>=', self.date_from),
                                                   ('date_from', '<=', self.date_to),
                                                   ('overtime_id.state', '=', 'finish')])
        # over time start in last month end finish in this month  or after
        overtime_lines2 = overtime_line_obj.search([('date_from', '<', self.date_from),
                                                    ('date_to', '>=', self.date_from),
                                                   ('overtime_id.state', '=', 'finish')])
        overtime_lines = list(set(overtime_lines1 + overtime_lines2))
        print '-'
        # TODO: dont compute not work days
        for overtime in overtime_lines:
            employee = overtime.employee_id
            salary_grid = employee.salary_grid_id
            #
            date_from = overtime.date_from
            date_to = overtime.date_to
            if overtime.date_from < self.date_from:
                date_from = self.date_from
            if overtime.date_to > self.date_to:
                date_to = self.date_to
            number_of_days = days_between(date_from, date_to)
            number_of_hours = 0.0
            if overtime.date_from >= self.date_from and overtime.date_to <= self.date_to:
                number_of_hours = overtime.heure_number
            # get number of hours
            total_hours = number_of_days * 7 + number_of_hours
            amount_hour = salary_grid.basic_salary / 22.0 / 7.0  # TODO: 22.0 and 7.0 : get it from worker days
            rate_hour = overtime_setting.normal_days
            if overtime.type == 'friday_saturday':
                rate_hour = overtime_setting.friday_saturday
            elif overtime.type == 'holidays':
                rate_hour = overtime_setting.holidays
            amount = amount_hour * rate_hour / 100.0 * total_hours
            overtime_val = {'difference_id': self.id,
                            'name': overtime_setting.allowance_overtime_id.name,
                            'employee_id': employee.id,
                            'number_of_days': number_of_days,
                            'number_of_hours': number_of_hours,
                            'amount': amount,
                            'type': 'overtime'}
            line_ids.append(overtime_val)
            # add allowance transport
            if number_of_days:
                # search amount transport from salary grid
                transport_allowance_id = self.env.ref('smart_hr.hr_allowance_type_01').id
                transport_allowances = grid_detail_allowance_obj.search([('grid_detail_id', '=', salary_grid.id), ('allowance_id', '=', transport_allowance_id)])
                transport_amount = 0.0
                if transport_allowances:
                    transport_amount = transport_allowances[0].get_value(employee.id) / 30.0 * number_of_days
                allowance_transport_val = {'difference_id': self.id,
                                           'name': overtime_setting.allowance_transport_id.name,
                                           'employee_id': employee.id,
                                           'number_of_days': number_of_days,
                                           'number_of_hours': number_of_hours,
                                           'amount': transport_amount,
                                           'type': 'overtime'}
                line_ids.append(allowance_transport_val)
        return line_ids

    @api.multi
    def get_difference_deputation(self):
        line_ids = []
        deputation_obj = self.env['hr.deputation']
        deputation_allowance_obj = self.env['hr.deputation.allowance']
        deputation_setting = self.env['hr.deputation.setting'].search([], limit=1)
        # deputation start in this month end finish in this month or after
        deputations1 = deputation_obj.search([('date_from', '>=', self.date_from),
                                              ('date_from', '<=', self.date_to),
                                              ('state', '=', 'finish')])
        # deputation start in last month end finish in this month  or after
        deputations2 = deputation_obj.search([('date_from', '<', self.date_from),
                                              ('date_to', '>=', self.date_from),
                                              ('state', '=', 'finish')])
        deputations = list(set(deputations1 + deputations2))
        for deputation in deputations:
            date_from = deputation.date_from
            date_to = deputation.date_to
            if deputation.date_from < self.date_from:
                date_from = self.date_from
            if deputation.date_to > self.date_to:
                date_to = self.date_to
            number_of_days = days_between(date_from, date_to)
            #
            employee = deputation.employee_id
            # get a correct line
            deputation_allowance_lines = deputation_allowance_obj.search([('grade_ids', 'in', [employee.grade_id.id])])
            if deputation_allowance_lines:
                deputation_allowance = deputation_allowance_lines[0]
                deputation_amount = 0.0
                transport_amount = 0.0
                if deputation.type == 'internal':
                    if deputation_allowance.internal_transport_type == 'daily':
                        transport_amount = deputation_allowance.internal_transport_amount * number_of_days
                    elif deputation_allowance.internal_transport_type == 'monthly':
                        transport_amount = deputation_allowance.internal_transport_amount
                    if deputation_allowance.internal_deputation_type == 'daily':
                        deputation_amount = deputation_allowance.internal_deputation_amount * number_of_days
                    elif deputation_allowance.internal_deputation_type == 'monthly':
                        deputation_amount = deputation_allowance.internal_deputation_amount
                elif deputation.type == 'external':
                    if deputation_allowance.external_transport_type == 'daily':
                        transport_amount = deputation_allowance.external_transport_amount * number_of_days
                    elif deputation_allowance.external_transport_type == 'monthly':
                        transport_amount = deputation_allowance.external_transport_amount
                    # search a correct category
                    searchs = deputation_allowance.category_ids.search([('category_id', '=', deputation.category_id.id)])
                    if searchs:
                        if deputation_allowance.external_deputation_type == 'daily':
                            deputation_amount = searchs[0].amount * number_of_days
                        elif deputation_allowance.internal_transport_type == 'monthly':
                            deputation_amount = searchs[0].amount
                # بدل نقل
                transport_val = {'difference_id': self.id,
                                 'name': deputation_allowance.allowance_transport_id.name,
                                 'employee_id': employee.id,
                                 'number_of_days': number_of_days,
                                 'number_of_hours': 0.0,
                                 'amount': transport_amount,
                                 'type': 'deputation'}
                line_ids.append(transport_val)
                deputation_amount_rate = 1.0
                if deputation.the_availability == 'hosing_and_food':
                    deputation_amount_rate = 0.25
                elif deputation.the_availability == 'hosing_or_food':
                    deputation_amount_rate = 0.5
                deputation_amount = deputation_amount * deputation_amount_rate
                # بدل إنتداب
                deputation_val = {'difference_id': self.id,
                                  'name': deputation_allowance.allowance_deputation_id.name,
                                  'employee_id': employee.id,
                                  'number_of_days': number_of_days,
                                  'number_of_hours': 0.0,
                                  'amount': deputation_amount,
                                  'type': 'deputation'}
                line_ids.append(deputation_val)
        return line_ids

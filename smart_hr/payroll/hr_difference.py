# -*- coding: utf-8 -*-

from openerp import models, api, fields, _
from openerp.exceptions import ValidationError
from dateutil import relativedelta
import time as time_date
from datetime import datetime
from openerp.addons.smart_base.util.time_util import days_between
from openerp.addons.smart_base.util.umalqurra import *
from umalqurra.hijri_date import HijriDate
from umalqurra.hijri import Umalqurra


class hrDifference(models.Model):
    _name = 'hr.difference'
    _inherit = ['mail.thread']
    _order = 'id desc'
    _description = u'الفروقات'

    @api.multi
    def get_default_month(self):
        return get_current_month_hijri(HijriDate)

    name = fields.Char(string=' المسمى', required=1, readonly=1, states={'new': [('readonly', 0)]})
    # TODO: get default MONTH
    month = fields.Selection(MONTHS, string='الشهر', required=1, readonly=1, states={'new': [('readonly', 0)]}, default=get_default_month)
    date = fields.Date(string='تاريخ الإنشاء', required=1, default=fields.Datetime.now(), readonly=1, states={'new': [('readonly', 0)]})
    date_from = fields.Date('تاريخ من', readonly=1, states={'new': [('readonly', 0)]})
    date_to = fields.Date('إلى', readonly=1, states={'new': [('readonly', 0)]})
    state = fields.Selection([('new', 'مسودة'),
                              ('waiting', 'في إنتظار الإعتماد'),
                              ('cancel', 'مرفوض'),
                              ('done', 'اعتمدت')], string='الحالة', readonly=1, default='new')
    line_ids = fields.One2many('hr.difference.line', 'difference_id', string='الفروقات', readonly=1, states={'new': [('readonly', 0)]})

    @api.onchange('month')
    def onchange_month(self):
        if self.month:
            self.date_from = get_hijri_month_start(HijriDate, Umalqurra, self.month)
            self.date_to = get_hijri_month_end(HijriDate, Umalqurra, self.month)
            self.name = u'فروقات شهر %s' % self.month
            line_ids = []
            # فروقات خارج الدوام
            line_ids += self.get_difference_overtime()
            # فروقات الأنتداب
            line_ids += self.get_difference_deputation()
            # فروقات النقل
            line_ids += self.get_difference_transfert()
            # فروقات التعين
            line_ids += self.get_difference_decision_appoint()
            # فروقات التكليف
            line_ids += self.get_difference_assign()
            # فروقات الإبتعاث
            line_ids += self.get_difference_scholarship()
            # فروقات الإعارة
            line_ids += self.get_difference_lend()
            # فروقات الإجازة
            line_ids += self.get_difference_holidays()
            # فروقات كف اليد
            line_ids += self.get_difference_suspension()
            # فروقات طى القيد
            line_ids += self.get_difference_termination()
            # فرق الحسميات أكثر من ثلث الراتب
            line_ids += self.get_difference_one_third_salary()
            # أوامر الإركاب
            line_ids += self.get_difference_transport_decision()
            self.line_ids = line_ids

    @api.model
    def create(self, vals):
        print '----vals-----', vals
        if 'product_id' in vals:
            vals['product_id'] = vals['product_id'][0]
        res = super(hrDifference, self).create(vals)
        return res

    @api.one
    def action_waiting(self):
        self.state = 'waiting'

    @api.multi
    def action_done(self):
        self.state = 'done'

    @api.one
    def action_refuse(self):
        self.state = 'cancel'

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

    @api.multi
    def get_difference_transfert(self):
        self.ensure_one()
        line_ids = []
        hr_setting = self.env['hr.setting'].search([], limit=1)
        if hr_setting:
            transfert_ids = self.env['hr.employee.transfert'].search([('create_date', '>=', self.date_from),
                                                                      ('create_date', '<=', self.date_to),
                                                                      ('state', '=', 'done')])
            for transfert in transfert_ids:
                # get تفاصيل سلم الرواتب
                grid_id = transfert.employee_id.salary_grid_id
                if grid_id:
                    # 1- بدل طبيعة العمل
                    amount = (hr_setting.allowance_proportion * grid_id.basic_salary)
                    if amount > 0:
                        amount = amount / 100
                    vals = {'difference_id': self.id,
                            'name': hr_setting.allowance_job_nature.name,
                            'employee_id': transfert.employee_id.id,
                            'number_of_days': 0,
                            'number_of_hours': 0.0,
                            'amount': amount,
                            'type': 'transfert'}
                    line_ids.append(vals)
                    # 2- بدل إنتداب
                    amount = (hr_setting.deputation_days * (grid_id.basic_salary / 22))
                    vals = {'difference_id': self.id,
                            'name': hr_setting.allowance_deputation.name,
                            'employee_id': transfert.employee_id.id,
                            'number_of_days': hr_setting.deputation_days,
                            'number_of_hours': 0.0,
                            'amount': amount,
                            'type': 'transfert'}
                    line_ids.append(vals)
                    # 3- بدل ترحيل
                    amount = (hr_setting.deportation_amount)
                    vals = {'difference_id': self.id,
                            'name': hr_setting.allowance_deportation.name,
                            'employee_id': transfert.employee_id.id,
                            'number_of_days': 0,
                            'number_of_hours': 0.0,
                            'amount': amount,
                            'type': 'transfert'}
                    line_ids.append(vals)
                    # 4- نسبة الراتب
                    if transfert.salary_proportion > 0:
                        amount = (((100 - transfert.salary_proportion) * grid_id.basic_salary) / 100) * -1
                        if amount < 0:
                            vals = {'difference_id': self.id,
                                    'name': u'فرق الراتب التي توفرها الجهة',
                                    'employee_id': transfert.employee_id.id,
                                    'number_of_days': 0,
                                    'number_of_hours': 0.0,
                                    'amount': amount,
                                    'type': 'transfert'}
                            line_ids.append(vals)
        return line_ids

    @api.multi
    def get_difference_decision_appoint(self):
        self.ensure_one()
        line_ids = []
        last_decision_appoint_ids = self.env['hr.decision.appoint'].search([('is_started', '=', True),
                                                                            ('state_appoint', '=', 'active'),
                                                                            ('date_direct_action', '>=', self.date_from),
                                                                            ('date_direct_action', '<=', self.date_to),
                                                                            ], order="date_direct_action desc")
        for last_decision_appoint_id in last_decision_appoint_ids:
            for allowance in last_decision_appoint_id.type_appointment.hr_allowance_appoint_id:
                amount = allowance.salary_number * last_decision_appoint_id.employee_id.salary_grid_id.basic_salary
                vals = {'difference_id': self.id,
                        'name': allowance.hr_allowance_type_id.name,
                        'employee_id': last_decision_appoint_id.employee_id.id,
                        'number_of_days': 0,
                        'number_of_hours': 0.0,
                        'amount': amount,
                        'type': 'appoint'}
                line_ids.append(vals)
        return line_ids

    @api.multi
    def get_difference_assign(self):
        self.ensure_one()
        line_ids = []
        assign_ids = self.env['hr.employee.commissioning'].search([('date_to', '>=', self.date_from),
                                                                   ('date_to', '<=', self.date_to),
                                                                   ('state', '=', 'done')])
        for assign_id in assign_ids:
            # get تفاصيل سلم الرواتب
            grid_id = assign_id.employee_id.salary_grid_id
            if grid_id:
                # تفاصيل سلم الرواتب
                allowance_ids = grid_id.allowance_ids
                reward_ids = grid_id.reward_ids
                indemnity_ids = grid_id.indemnity_ids
                # راتب
                if assign_id.give_salary:
                    amount = grid_id.basic_salary
                    if amount:
                            vals = {'difference_id': self.id,
                                    'name': 'فرق الراتب التي توفرها الجهة',
                                    'employee_id': assign_id.employee_id.id,
                                    'number_of_days': 0,
                                    'number_of_hours': 0.0,
                                    'amount': amount * -1,
                                    'type': 'commissioning'}
                            line_ids.append(vals)
                # بدل النقل
                if assign_id.give_allowance_transport:
                    allowance_transport_id = self.env.ref('smart_hr.hr_allowance_type_01')
                    if allowance_transport_id:
                        amount = 0.0
                        for allow in allowance_ids:
                            if allow.allowance_id == allowance_transport_id:
                                amount = allow.get_value(assign_id.employee_id.id)
                                break
                        if amount:
                            vals = {'difference_id': self.id,
                                    'name': 'فرق بدل النقل الذي توفره الجهة',
                                    'employee_id': assign_id.employee_id.id,
                                    'number_of_days': 0,
                                    'number_of_hours': 0.0,
                                    'amount': amount * -1,
                                    'type': 'commissioning'}
                            line_ids.append(vals)
                # بدلات، مكافأة أو تعويضات
                if assign_id.give_allow:
                    # بدلات
                    for allow in allowance_ids:
                        if allow.allowance_id != self.env.ref('smart_hr.hr_allowance_type_01'):
                            amount = allow.get_value(assign_id.employee_id.id)
                            if amount:
                                vals = {'difference_id': self.id,
                                        'name': allow.allowance_id.name,
                                        'employee_id': assign_id.employee_id.id,
                                        'number_of_days': 0,
                                        'number_of_hours': 0.0,
                                        'amount': amount * -1,
                                        'type': 'commissioning'}
                                line_ids.append(vals)
                    # مكافأة
                    for reward in reward_ids:
                        amount = reward.get_value(assign_id.employee_id.id)
                        if amount:
                            vals = {'difference_id': self.id,
                                    'name': reward.reward_id.name,
                                    'employee_id': assign_id.employee_id.id,
                                    'number_of_days': 0,
                                    'number_of_hours': 0.0,
                                    'amount': amount * -1,
                                    'type': 'commissioning'}
                            line_ids.append(vals)
                    # تعويضات
                    for indemnity in indemnity_ids:
                        amount = indemnity.get_value(assign_id.employee_id.id)
                        if amount:
                            vals = {'difference_id': self.id,
                                    'name': indemnity.indemnity_id.name,
                                    'employee_id': assign_id.employee_id.id,
                                    'number_of_days': 0,
                                    'number_of_hours': 0.0,
                                    'amount': amount * -1,
                                    'type': 'commissioning'}
                            line_ids.append(vals)
        return line_ids

    @api.multi
    def get_difference_scholarship(self):
        self.ensure_one()
        line_ids = []
        scholarship_ids = self.env['hr.scholarship'].search([('date_to', '>=', self.date_from),
                                                             ('date_to', '<=', self.date_to),
                                                             ('state', '=', 'done')
                                                             ])
        for scholarship_id in scholarship_ids:
            grid_id = scholarship_id.employee_id.salary_grid_id
            if grid_id:
                # 1) البدلات المستثناة
                alowances_in_grade_id = [rec.allowance_id for rec in grid_id.allowance_ids]
                for allowance in scholarship_id.hr_allowance_type_id:
                    # check if the allowance in employe's salary_grade_id
                    if allowance in alowances_in_grade_id:
                        amount = 0.0
                        for allow in grid_id.allowance_ids:
                            if allow.allowance_id == allowance:
                                amount = allow.get_value(scholarship_id.employee_id.id)
                                break
                        if amount > 0:
                            vals = {'difference_id': self.id,
                                    'name': allowance.name,
                                    'employee_id': scholarship_id.employee_id.id,
                                    'number_of_days': 0.0,
                                    'number_of_hours': 0.0,
                                    'amount': amount * -1,
                                    'type': 'scholarship'}
                            line_ids.append(vals)
                # 2) نسبة الراتب
                amount = grid_id.basic_salary - ((grid_id.basic_salary * scholarship_id.salary_percent) / 100.0)
                if amount > 0:
                    vals = {'difference_id': self.id,
                            'name': allowance.name,
                            'employee_id': scholarship_id.employee_id.id,
                            'number_of_days': 0.0,
                            'number_of_hours': 0.0,
                            'amount': amount * -1,
                            'type': 'scholarship'}
                    line_ids.append(vals)
        return line_ids

    @api.multi
    def get_difference_lend(self):
        self.ensure_one()
        line_ids = []
        lend_ids = self.env['hr.employee.lend'].search([('state', '=', 'done')
                                                        ])
        for lend_id in lend_ids:
            # overlaped days in current month
            lend_date_from = fields.Date.from_string(lend_id.date_from)
            date_from = fields.Date.from_string(self.date_from)
            lend_date_to = fields.Date.from_string(lend_id.date_to)
            date_to = fields.Date.from_string(self.date_to)
            duration_in_month = 0
            if date_from >= lend_date_from and lend_date_to >= date_to:
                duration_in_month = self.env['hr.smart.utils'].compute_duration(date_from, date_to)
            if lend_date_from >= date_from and lend_date_to <= date_to:
                duration_in_month = self.env['hr.smart.utils'].compute_duration(lend_date_to, lend_date_from)
            if lend_date_from >= date_from and lend_date_to >= date_to:
                duration_in_month = self.env['hr.smart.utils'].compute_duration(date_to, lend_date_from)
            grid_id = lend_id.employee_id.salary_grid_id
            if grid_id and duration_in_month > 0:
                # 1) نسبة الراتب
                amount = ((duration_in_month * (grid_id.basic_salary / 22) * lend_id.salary_proportion) / 100.0) * -1
                if amount < 0:
                    vals = {'difference_id': self.id,
                            'name': 'نسبة الراتب',
                            'employee_id': lend_id.employee_id.id,
                            'number_of_days': duration_in_month,
                            'number_of_hours': 0.0,
                            'amount': amount,
                            'type': 'lend'}
                    line_ids.append(vals)
                # 2) البدلات في الإعارة
                alowances_in_grade_id = [rec.allowance_id for rec in grid_id.allowance_ids]
                for allowance in lend_id.allowance_ids:
                    if allowance not in alowances_in_grade_id:
                        vals = {'difference_id': self.id,
                                'name': allowance.allowance_id.name,
                                'employee_id': lend_id.employee_id.id,
                                'number_of_days': duration_in_month,
                                'number_of_hours': 0.0,
                                'amount': allowance.amount,
                                'type': 'lend'}
                        line_ids.append(vals)
                # 3) حصة الحكومة من التقاعد
                if lend_id.pay_retirement:
                    hr_setting = self.env['hr.setting'].search([], limit=1)
                    if hr_setting:
                        amount = (grid_id.basic_salary * hr_setting.retirement_proportion) / 100.0
                        if amount > 0:
                            vals = {'difference_id': self.id,
                                    'name': 'حصة الحكومة من التقاعد',
                                    'employee_id': lend_id.employee_id.id,
                                    'number_of_days': duration_in_month,
                                    'number_of_hours': 0.0,
                                    'amount': amount,
                                    'type': 'lend'}
                            line_ids.append(vals)
                # 4) فرق الراتب
                amount = ((lend_id.lend_salary - lend_id.basic_salary) / 22) * duration_in_month
                if amount > 0:
                    vals = {'difference_id': self.id,
                            'name': 'فرق الراتب',
                            'employee_id': lend_id.employee_id.id,
                            'number_of_days': duration_in_month,
                            'number_of_hours': 0.0,
                            'amount': amount,
                            'type': 'lend'}
                    line_ids.append(vals)
        return line_ids

    @api.multi
    def get_difference_holidays(self):
        self.ensure_one()
        line_ids = []
        holidays_ids = self.env['hr.holidays'].search([('date_to', '>=', self.date_from),
                                                       ('date_to', '<=', self.date_to),
                                                       ('state', '=', 'done')
                                                       ])
        for holiday_id in holidays_ids:
            # token days in current month
            holiday_date_from = fields.Date.from_string(holiday_id.date_from)
            date_from = fields.Date.from_string(self.date_from)
            holiday_date_to = fields.Date.from_string(holiday_id.date_to)
            date_to = fields.Date.from_string(self.date_to)
            days = self.env['hr.smart.utils'].compute_duration(holiday_date_from, date_from)
            today = fields.Date.from_string(fields.Date.today())
            months_from_holiday_start = relativedelta.relativedelta(today, holiday_date_from).months
            # days in current month
            if days < 0 and holiday_date_to <= date_to:
                duration_in_month = self.env['hr.smart.utils'].compute_duration(holiday_date_to, date_from)
            if days < 0 and holiday_date_to > date_to:
                duration_in_month = self.env['hr.smart.utils'].compute_duration(date_to, date_from)
            if days >= 0 and holiday_date_to <= date_to:
                duration_in_month = self.env['hr.smart.utils'].compute_duration(holiday_date_to, holiday_date_from)
            if days >= 0 and holiday_date_to > date_to:
                duration_in_month = self.env['hr.smart.utils'].compute_duration(date_to, holiday_date_from)
            grid_id = holiday_id.employee_id.salary_grid_id
            holiday_status_id = holiday_id.holiday_status_id
            # get the entitlement type
            if not holiday_id.entitlement_type:
                entitlement_type = self.env.ref('smart_hr.data_hr_holiday_entitlement_all')
            else:
                entitlement_type = holiday_id.entitlement_type
            print entitlement_type
            if grid_id and holiday_status_id.salary_spending:
                for rec in holiday_status_id.percentages:
                    if entitlement_type == rec.entitlement_id and months_from_holiday_start >= rec.month_from and months_from_holiday_start <= rec.month_to:
                        amount = (((duration_in_month * (grid_id.basic_salary / 22)) * (100 - rec.salary_proportion))) / 100.0
                        vals = {'difference_id': self.id,
                                'name': holiday_id.holiday_status_id.name,
                                'employee_id': holiday_id.employee_id.id,
                                'number_of_days': duration_in_month,
                                'number_of_hours': 0.0,
                                'amount': (amount) * -1,
                                'type': 'holiday'}
                        line_ids.append(vals)
        return line_ids

    @api.multi
    def get_difference_suspension(self):
        self.ensure_one()
        line_ids = []
        suspension_end_ids = self.env['hr.suspension.end'].search([('date', '>=', self.date_from),
                                                                   ('date', '<=', self.date_to),
                                                                   ('state', '=', 'done')
                                                                   ])
        for suspension_end in suspension_end_ids:
            # case there is condemned for the employee
            if suspension_end.condemned:
                date_from = fields.Date.from_string(self.date_from)
                if suspension_end.suspension_id.suspension_date > self.date_from:
                    date_from = fields.Date.from_string(suspension_end.suspension_id.suspension_date)
                date_to = fields.Date.from_string(suspension_end.release_date)
                days = self.env['hr.smart.utils'].compute_duration(date_to, date_from)
                grid_id = suspension_end.employee_id.salary_grid_id
                if grid_id:
                    amount = (grid_id.basic_salary / 22) * days
                    vals = {'difference_id': self.id,
                            'name': 'فرق كف اليد',
                            'employee_id': suspension_end.employee_id.id,
                            'number_of_days': days,
                            'number_of_hours': 0.0,
                            'amount': amount * -1,
                            'type': 'suspension'}
                    line_ids.append(vals)
            if not suspension_end.condemned:
                if suspension_end.suspension_id.suspension_date < self.date_from:
                    date_from = fields.Date.from_string(suspension_end.suspension_id.suspension_date)
                    date_to = fields.Date.from_string(self.date_from)
                    days = self.env['hr.smart.utils'].compute_duration(date_to, date_from) - 1
                    grid_id = suspension_end.employee_id.salary_grid_id
                    if grid_id:
                        # الراتب الأساسي
                        amount = (grid_id.basic_salary / 22) * days
                        vals = {'difference_id': self.id,
                                'name': 'فرق الراتب الأساسي كف اليد',
                                'employee_id': suspension_end.employee_id.id,
                                'number_of_days': days,
                                'number_of_hours': 0.0,
                                'amount': amount,
                                'type': 'suspension'}
                        line_ids.append(vals)
                        # 2- البدلات القارة
                        for allowance in grid_id.allowance_ids:
                            amount = allowance.get_value(suspension_end.employee_id.id) / 22.0 * days
                            allowance_val = {'difference_id': self.id,
                                             'name': 'فرق %s كف اليد' % allowance.allowance_id.name,
                                             'employee_id': suspension_end.employee_id.id,
                                             'number_of_days': days,
                                             'number_of_hours': 0.0,
                                             'amount': amount,
                                             'type': 'suspension'}
                            line_ids.append(allowance_val)
                        for reward in grid_id.reward_ids:
                            amount = reward.get_value(suspension_end.employee_id.id) / 22.0 * days
                            reward_val = {'difference_id': self.id,
                                          'name': 'فرق %s كف اليد' % reward.reward_id.name,
                                          'employee_id': suspension_end.employee_id.id,
                                          'number_of_days': days,
                                          'number_of_hours': 0.0,
                                          'amount': amount,
                                          'type': 'suspension'}
                            line_ids.append(reward_val)
                        for indemnity in grid_id.indemnity_ids:
                            amount = indemnity.get_value(suspension_end.employee_id.id) / 22.0 * days
                            indemnity_val = {'difference_id': self.id,
                                             'name': 'فرق %s كف اليد' % indemnity.indemnity_id.name,
                                             'employee_id': suspension_end.employee_id.id,
                                             'number_of_days': days,
                                             'number_of_hours': 0.0,
                                             'amount': amount,
                                             'type': 'suspension'}
                            line_ids.append(indemnity_val)
        return line_ids

    @api.multi
    def get_difference_termination(self):
        self.ensure_one()
        line_ids = []
        termination_ids = self.env['hr.termination'].search([('date', '>=', self.date_from),
                                                             ('date', '<=', self.date_to),
                                                             ('state', '=', 'done')
                                                             ])
        for termination in termination_ids:
            grid_id = termination.employee_id.salary_grid_id
            # سعودي
            if termination.employee_id.country_id and termination.employee_id.country_id.code == 'SA':
                if grid_id:
                    # 1) عدد الرواتب المستحق
                    if termination.termination_type_id.nb_salaire > 0:
                        amount = (grid_id.basic_salary) * (termination.termination_type_id.nb_salaire - 1)
                        vals = {'difference_id': self.id,
                                'name': termination.termination_type_id.name + " " + u'(عدد الرواتب)',
                                'employee_id': termination.employee_id.id,
                                'number_of_days': (termination.termination_type_id.nb_salaire - 1) * 22,
                                'number_of_hours': 0.0,
                                'amount': (amount),
                                'type': 'termination'}
                        line_ids.append(vals)
            sum_days = 0
            for rec in termination.employee_id.holidays_balance:
                sum_days += rec.holidays_available_stock
            # 2) الإجازة
            if not termination.termination_type_id.all_holidays and sum_days >= termination.termination_type_id.max_days:
                if grid_id:
                    amount = (grid_id.basic_salary / 22) * (termination.termination_type_id.max_days)
                    if amount != 0.0: 
                        vals = {'difference_id': self.id,
                                'name': 'رصيد إجازة (طي القيد)',
                                'employee_id': termination.employee_id.id,
                                'number_of_days': termination.termination_type_id.max_days,
                                'number_of_hours': 0.0,
                                'amount': (amount),
                                'type': 'termination'}
                        line_ids.append(vals)
            if termination.termination_type_id.all_holidays and sum_days > 0:
                if grid_id:
                    amount = (grid_id.basic_salary / 22) * (sum_days)
                    if amount != 0.0:
                        vals = {'difference_id': self.id,
                                'name': 'رصيد إجازة (طي القيد)',
                                'employee_id': termination.employee_id.id,
                                'number_of_days': sum_days,
                                'number_of_hours': 0.0,
                                'amount': (amount),
                                'type': 'termination'}
                        line_ids.append(vals)
        return line_ids

    @api.multi
    def get_difference_one_third_salary(self):
        self.ensure_one()
        line_ids = []
        difference_history_ids = self.env['hr.payslip.difference.history'].search([('month', '=', fields.Date.from_string(self.date_from).month)])
        for difference_history in difference_history_ids:
            grid_id = difference_history.employee_id.salary_grid_id
            if grid_id:
                vals = {'difference_id': self.id,
                        'name': 'فرق الحسميات أكثر من ثلث الراتب',
                        'employee_id': difference_history.employee_id.id,
                        'number_of_days': 0.0,
                        'number_of_hours': 0.0,
                        'amount': (difference_history.amount),
                        'type': 'one_third_salary'}
                line_ids.append(vals)
        return line_ids

    @api.multi
    def get_difference_transport_decision(self):
        self.ensure_one()
        line_ids = []
        transfert_decision_ids = self.env['hr.transport.decision'].search([('order_date', '>=', self.date_from),
                                                                           ('order_date', '<=', self.date_to),
                                                                           ('state', 'in', ['done', 'finish'])
                                                                           ])
        for transfert_decision in transfert_decision_ids:
            vals = {'difference_id': self.id,
                    'name': 'فرق أمر اركاب',
                    'employee_id': transfert_decision.employee_id.id,
                    'number_of_days': 0.0,
                    'number_of_hours': 0.0,
                    'amount': (transfert_decision.amount),
                    'type': 'transfert_decision'}
            line_ids.append(vals)
        return line_ids


class hrDifferenceLine(models.Model):
    _name = 'hr.difference.line'

    difference_id = fields.Many2one('hr.difference', string=' الفروقات', ondelete='cascade')
    name = fields.Char(string=' المسمى')
    employee_id = fields.Many2one('hr.employee', string='الموظف')
    job_id = fields.Many2one(related='employee_id.job_id', store=True, readonly=True, string=' الوظيفة')
    department_id = fields.Many2one(related='employee_id.department_id', store=True, readonly=True, string=' الادارة')
    amount = fields.Float(string='المبلغ')
    number_of_days = fields.Float(string='عدد الأيام')
    number_of_hours = fields.Float(string='عدد الساعات')
    month = fields.Selection(MONTHS, related='difference_id.month', store=True, readonly=True, string='الشهر')
    # TODO: do the store for state
    state = fields.Selection(related='difference_id.state', string='الحالة')
    # TODO: , النقل توظيف
    type = fields.Selection([('increase', 'علاوة'),
                             ('promotion', 'ترقية'),
                             ('scholarship', 'ابتعاث'),
                             ('appoint', 'تعيين'),
                             ('lend', 'إعارة'),
                             ('termination', 'طى القيد'),
                             ('holiday', 'إجازة'),
                             ('commissioning', 'تكليف'),
                             ('deputation', 'إنتداب'),
                             ('overtime', 'خارج الدوام'),
                             ('suspension', 'كف اليد'),
                             ('transfert', 'نقل'),
                             ('transfert_decision', 'اركاب'),
                             ('one_third_salary', 'ثلث راتب'),
                             ('training', 'تدريب')], string='النوع', readonly=1)

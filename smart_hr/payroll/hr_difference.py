# -*- coding: utf-8 -*-

from openerp import models, api, fields, _
from openerp.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
import time as time_date
from datetime import datetime
from openerp.addons.smart_base.util.time_util import days_between
from openerp.addons.smart_base.util.umalqurra import *
from umalqurra.hijri_date import HijriDate
from umalqurra.hijri import Umalqurra


class HrDifference(models.Model):
    _name = 'hr.difference'
    _inherit = ['mail.thread']
    _order = 'id desc'
    _description = u'الفروقات'

    @api.multi
    def get_default_month(self):
        return get_current_month_hijri(HijriDate)

    name = fields.Char(string=' المسمى', required=1, readonly=1, states={'new': [('readonly', 0)]})
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
        if 'product_id' in vals:
            vals['product_id'] = vals['product_id'][0]
        res = super(HrDifference, self).create(vals)
        return res

    @api.one
    def action_waiting(self):
        self.state = 'waiting'

    @api.multi
    def action_done(self):
        self.state = 'done'

    @api.one
    def button_refuse(self):
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
            salary_grid, basic_salary = employee.get_salary_grid_id(False)
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
            amount_hour = basic_salary / 30.0 / 7.0
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
            deputation_amount, transport_amount, deputation_allowance = deputation.get_deputation_allowance_amount(number_of_days)
            if transport_amount:
                # بدل نقل
                transport_val = {'difference_id': self.id,
                                 'name': deputation_allowance.allowance_transport_id.name,
                                 'employee_id': employee.id,
                                 'number_of_days': number_of_days,
                                 'number_of_hours': 0.0,
                                 'amount': transport_amount,
                                 'type': 'deputation'}
                line_ids.append(transport_val)
            if deputation_amount:
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
                grid_id, basic_salary = transfert.employee_id.get_salary_grid_id(transfert.create_date)
                if grid_id:
                    # 1- بدل طبيعة العمل
                    amount = (hr_setting.allowance_proportion * basic_salary)
                    if amount > 0:
                        amount /= 100
                    vals = {'difference_id': self.id,
                            'name': hr_setting.allowance_job_nature.name,
                            'employee_id': transfert.employee_id.id,
                            'number_of_days': 0,
                            'number_of_hours': 0.0,
                            'amount': amount,
                            'type': 'transfert'}
                    line_ids.append(vals)
                    # 2- بدل إنتداب
                    amount = (hr_setting.deputation_days * (basic_salary / 22))
                    vals = {'difference_id': self.id,
                            'name': hr_setting.allowance_deputation.name,
                            'employee_id': transfert.employee_id.id,
                            'number_of_days': hr_setting.deputation_days,
                            'number_of_hours': 0.0,
                            'amount': amount,
                            'type': 'transfert'}
                    line_ids.append(vals)
                    # 3- بدل ترحيل
                    amount = hr_setting.deportation_amount
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
                        amount = (((100 - transfert.salary_proportion) * basic_salary) / 100) * -1
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
        for decision_appoint in last_decision_appoint_ids:
            grid_id, basic_salary = decision_appoint.employee_id.get_salary_grid_id(decision_appoint.date_direct_action)
            if grid_id:
                for allowance in decision_appoint.type_appointment.hr_allowance_appoint_id:
                    amount = allowance.salary_number * basic_salary
                    vals = {'difference_id': self.id,
                            'name': ' فروقات ' + decision_appoint.type_appointment.name + ' : ' + allowance.hr_allowance_type_id.name,
                            'employee_id': decision_appoint.employee_id.id,
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
            grid_id, basic_salary = assign_id.employee_id.get_salary_grid_id(assign_id.date_to)
            if grid_id:
                # تفاصيل سلم الرواتب
                allowance_ids = grid_id.allowance_ids
                reward_ids = grid_id.reward_ids
                indemnity_ids = grid_id.indemnity_ids
                # راتب
                if assign_id.give_salary:
                    amount = basic_salary
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
                # 3) حصة الحكومة من التقاعد
                if assign_id.comm_type.pay_retirement:
                    amount = (basic_salary * assign_id.retirement_proportion) / 100.0
                    if amount > 0:
                        vals = {'difference_id': self.id,
                                'name': 'حصة الحكومة من التقاعد',
                                'employee_id': assign_id.employee_id.id,
                                'number_of_days': 0,
                                'number_of_hours': 0.0,
                                'amount': amount,
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
            grid_id, basic_salary = scholarship_id.employee_id.get_salary_grid_id(scholarship_id.date_to)
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
                amount = basic_salary - ((basic_salary * scholarship_id.salary_percent) / 100.0)
                if amount > 0:
                    vals = {'difference_id': self.id,
                            'name': u'نسبة الراتب',
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
            grid_id, basic_salary = lend_id.employee_id.get_salary_grid_id(False)
            if grid_id and duration_in_month > 0:
                # 1) نسبة الراتب
                amount = ((duration_in_month * (basic_salary / 22) * lend_id.salary_proportion) / 100.0) * -1
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
                        amount = (basic_salary * hr_setting.retirement_proportion) / 100.0
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
            holiday_date_from = holiday_id.date_from
            date_from = self.date_from
            holiday_date_to = holiday_id.date_to
            date_to = self.date_to
            days = days_between(holiday_id.date_from, date_from)
            today = fields.Date.from_string(fields.Date.today())
            months_from_holiday_start = relativedelta(today, fields.Date.from_string(holiday_id.date_from)).months
            # days in current month
            if days < 0 and holiday_id.date_to <= self.date_to:
                duration_in_month = days_between(date_from, holiday_date_to)
            if days < 0 and holiday_id.date_to > self.date_to:
                duration_in_month = days_between(date_from, date_to)
            if days >= 0 and holiday_id.date_to <= self.date_to:
                duration_in_month = days_between(holiday_date_from, holiday_date_to)
            if days >= 0 and holiday_id.date_to > self.date_to:
                duration_in_month = days_between(holiday_date_from, date_to)
            duration_in_month -= 1
            grid_id, basic_salary = holiday_id.employee_id.get_salary_grid_id(False)
            holiday_status_id = holiday_id.holiday_status_id
            # get the entitlement type
            if not holiday_id.entitlement_type:
                entitlement_type = self.env.ref('smart_hr.data_hr_holiday_entitlement_all')
            else:
                entitlement_type = holiday_id.entitlement_type
            # case of لا يصرف له الراتب
            if grid_id and not holiday_status_id.salary_spending:
                amount = (duration_in_month * (basic_salary / 22))
                if duration_in_month > 0 and amount != 0:
                    vals = {'difference_id': self.id,
                            'name': holiday_id.holiday_status_id.name,
                            'employee_id': holiday_id.employee_id.id,
                            'number_of_days': duration_in_month,
                            'number_of_hours': 0.0,
                            'amount': amount * -1,
                            'type': 'holiday'}
                    line_ids.append(vals)
            # case of يصرف له الراتب
            if grid_id and holiday_status_id.salary_spending:
                for rec in holiday_status_id.percentages:
                    if entitlement_type == rec.entitlement_id.entitlment_category and rec.month_from <= months_from_holiday_start <= rec.month_to:
                        amount = (duration_in_month * (basic_salary / 22) * 100 - rec.salary_proportion) / 100.0
                        if amount != 0:
                            vals = {'difference_id': self.id,
                                    'name': holiday_id.holiday_status_id.name,
                                    'employee_id': holiday_id.employee_id.id,
                                    'number_of_days': duration_in_month,
                                    'number_of_hours': 0.0,
                                    'amount': amount * -1,
                                    'type': 'holiday'}
                            line_ids.append(vals)
            # case of  نوع التعويض    مقابل ‫مادي‬ ‬   اجازة التعويض
            if grid_id:
                if holiday_id.compensation_type and holiday_id.compensation_type == 'money':
                    print '------holiday_id.current_holiday_stock------', holiday_id.token_compensation_stock
                    print '------basic_salary--------', basic_salary
                    amount = (holiday_id.token_compensation_stock * (basic_salary / 22))
                    if amount != 0:
                        vals = {'difference_id': self.id,
                                'name': holiday_id.holiday_status_id.name + u"(تعويض مالي)",
                                'employee_id': holiday_id.employee_id.id,
                                'number_of_days': int(holiday_id.current_holiday_stock),
                                'number_of_hours': 0.0,
                                'amount': amount,
                                'type': 'holiday'}
                        line_ids.append(vals)
        return line_ids

    @api.multi
    def get_difference_suspension(self):
        # # إذا كان كف اليد على كامل الشهر الحالي فيجب احتساب الفرق على أساس  30 يوم   وإلا فيحتسب على عدد أيام الكف.
        # إذا كان عدد أيام الشهر أصغر من 30 يتم احتساب قيمة أيام فرق  مساوي إلى قيمة أخر يوم في الشهر.
        # مثلا شهر فيه 28 يوم يكون  قيمة يوم 29 و-30 مساوي لقيمة يوم 28.

        date_start_month = str(get_hijri_month_start(HijriDate, Umalqurra, self.month))
        date_end_month = str(get_hijri_month_end(HijriDate, Umalqurra, self.month))

        def _all_days_in_month(date_from, date_to):
            if date_start_month >= date_from and date_end_month <= date_to:
                return True
            return False

        self.ensure_one()
        line_ids = []
        all_suspensions = []
        # get  started and ended suspension in current month
        suspension_ids = self.env['hr.suspension'].search([('suspension_date', '>=', self.date_from),
                                                           ('suspension_date', '<=', self.date_to),
                                                           ('state', '=', 'done'),
                                                           ('suspension_end_id.release_date', '>=', self.date_from),
                                                           ('suspension_end_id.release_date', '<=', self.date_to),
                                                           ('suspension_end_id.state', '=', 'done'),
                                                           ])
        for suspension in suspension_ids:
            date_from = suspension.suspension_date
            date_to = suspension.suspension_end_id.release_date
            if date_from < self.date_from:
                date_from = self.date_from
            if date_to > self.date_to:
                date_to = self.date_to
            number_of_days = days_between(date_from, date_to)
            if number_of_days > 0 and suspension.suspension_end_id.condemned:
                all_suspensions.append({'employee_id': suspension.employee_id.id,
                                        'date_from': date_from, 'date_to': date_to,
                                        'number_of_days': number_of_days, 'return': False})

        # get started suspension in this month and not ended in current month or dont have yet an end
        suspension_ids = self.env['hr.suspension'].search([('suspension_date', '>=', self.date_from),
                                                           ('suspension_date', '<=', self.date_to),
                                                           ('state', '=', 'done'),
                                                           ('suspension_end_id', '=', False)
                                                           ])
        suspension_ids += self.env['hr.suspension'].search([('suspension_date', '>=', self.date_from),
                                                            ('suspension_date', '<=', self.date_to),
                                                            ('state', '=', 'done'),
                                                            ('suspension_end_id.release_date', '>', self.date_to),
                                                            ('suspension_end_id.state', '=', 'done'),
                                                            ])
        for suspension in suspension_ids:
            date_from = suspension.suspension_date
            date_to = self.date_to
            number_of_days = days_between(date_from, date_to)
            if number_of_days > 0:
                all_suspensions.append({'employee_id': suspension.employee_id.id,
                                        'date_from': date_from, 'date_to': date_to,
                                        'number_of_days': number_of_days, 'return': False})
        # get started suspension before this month and not yet ended
        suspension_ids = self.env['hr.suspension'].search([('suspension_date', '<', self.date_from),
                                                           ('state', '=', 'done'),
                                                           ('suspension_end_id', '=', False)
                                                           ])
        suspension_ids += self.env['hr.suspension'].search([('suspension_date', '<', self.date_from),
                                                            ('state', '=', 'done'),
                                                            ('suspension_end_id.release_date', '>', self.date_to),
                                                            ('suspension_end_id.state', '=', 'done'),
                                                            ])
        for suspension in suspension_ids:
            date_from = self.date_from
            date_to = self.date_to
            number_of_days = days_between(date_from, date_to)
            if number_of_days > 0:
                all_suspensions.append({'employee_id': suspension.employee_id.id,
                                        'date_from': date_from, 'date_to': date_to,
                                        'number_of_days': number_of_days, 'return': False})
        # get started suspension before this month and ended in current month
        suspension_ids = self.env['hr.suspension'].search([('suspension_date', '<', self.date_from),
                                                           ('state', '=', 'done'),
                                                           ('suspension_end_id.release_date', '>=', self.date_from),
                                                           ('suspension_end_id.release_date', '<=', self.date_to),
                                                           ('suspension_end_id.state', '=', 'done'),
                                                           ])
        for suspension in suspension_ids:
            # case 1: condemned
            if suspension.suspension_end_id.condemned:
                date_from = self.date_from
                date_to = suspension.suspension_end_id.release_date
                number_of_days = days_between(date_from, date_to)
                if number_of_days > 0:
                    all_suspensions.append({'employee_id': suspension.employee_id.id,
                                            'date_from': date_from, 'date_to': date_to,
                                            'number_of_days': number_of_days, 'return': False})
            # case 1: not condemned:
            else:
                date_from = suspension.suspension_date
                date_to = suspension.suspension_end_id.release_date
                number_of_days = days_between(date_from, date_to)
                if number_of_days > 0:
                    all_suspensions.append({'employee_id': suspension.employee_id.id,
                                            'date_from': date_from, 'date_to': date_to,
                                            'number_of_days': number_of_days, 'return': True})
        # احتساب الفروقات
        for suspension in all_suspensions:

            employee = self.env['hr.employee'].browse(suspension['employee_id'])
            suspension_number_of_days = suspension['number_of_days']
            number_of_days = suspension_number_of_days
            # 1- الراتب الأساسي : احتساب نصف الراتب الأساسي
            # must browse interval date from, date to to get the correct basic_salary for each date
            amount = 0.0
            multiplication = -1.0
            if suspension['return']:
                multiplication = 1.0
            date_start = datetime.strptime(suspension['date_from'], '%Y-%m-%d')
            while date_start.strftime('%Y-%m-%d') <= suspension['date_to']:
                salary_grid, basic_salary = employee.get_salary_grid_id(date_start.strftime('%Y-%m-%d'))
                amount += basic_salary / 30.0 / 2.0
                date_start = date_start + relativedelta(days=1)
            if _all_days_in_month(suspension['date_from'], suspension['date_to']):
                number_of_days = 30.0
                amount += (30 - suspension_number_of_days) * basic_salary / 30.0 / 2.0
            val = {'difference_id': self.id,
                   'name': 'فرق الراتب الأساسي كف اليد',
                   'employee_id': employee.id,
                   'number_of_days': number_of_days,
                   'number_of_hours': 0.0,
                   'amount': amount * multiplication,
                   'type': 'suspension'}
            line_ids.append(val)
            # 2- البدلات لا تحتسب في حال كان الموظف مكفوف اليد
            salary_grid, basic_salary = employee.get_salary_grid_id(date_start.strftime('%Y-%m-%d'))
            if not suspension['return']:
                for allowance in salary_grid.allowance_ids:
                    allowance_amount = 0.0
                    date_start = datetime.strptime(suspension['date_from'], '%Y-%m-%d')
                    while date_start.strftime('%Y-%m-%d') <= suspension['date_to']:
                        allowance_val = allowance.get_value(employee.id) / 30.0
                        allowance_amount += allowance_val
                        date_start = date_start + relativedelta(days=1)
                    if _all_days_in_month(suspension['date_from'], suspension['date_to']):
                        number_of_days = 30.0
                        allowance_amount += (30 - suspension_number_of_days) * allowance_val
                    val = {'difference_id': self.id,
                           'name': 'فرق %s كف اليد' % allowance.allowance_id.name,
                           'employee_id': employee.id,
                           'number_of_days': number_of_days,
                           'number_of_hours': 0.0,
                           'amount': allowance_amount * multiplication,
                           'type': 'suspension'}
                    line_ids.append(val)
                    # TODO: add reward_ids and indemnity_ids

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
            grid_id, basic_salary = termination.employee_id.get_salary_grid_id(termination.date)
            if grid_id:
                # فرق الأيام المخصومة من الشهر
                date_from = self.date_from
                date_to = termination.date
                worked_days = days_between(date_from, date_to) - 1
                unworked_days = 22 - worked_days
                if unworked_days > 0:
                    amount = (basic_salary / 22.0) * unworked_days
                    vals = {'difference_id': self.id,
                            'name': termination.termination_type_id.name + " " + u'(فرق الأيام المخصومة من الشهر)',
                            'employee_id': termination.employee_id.id,
                            'number_of_days': unworked_days,
                            'number_of_hours': 0.0,
                            'amount': amount * -1,
                            'type': 'termination'}
                    line_ids.append(vals)
            # سعودي
            if termination.employee_id.country_id and termination.employee_id.country_id.code == 'SA':
                if grid_id:
                    if termination.employee_id.basic_salary == 0:
                        basic_salary = grid_id.basic_salary
                    else:
                        basic_salary = termination.employee_id.basic_salary
                    # 1) عدد الرواتب المستحق
                    if termination.termination_type_id.nb_salaire > 0:
                        amount = basic_salary * (termination.termination_type_id.nb_salaire - 1)
                        vals = {'difference_id': self.id,
                                'name': termination.termination_type_id.name + " " + u'(عدد الرواتب)',
                                'employee_id': termination.employee_id.id,
                                'number_of_days': (termination.termination_type_id.nb_salaire - 1) * 22,
                                'number_of_hours': 0.0,
                                'amount': amount,
                                'type': 'termination'}
                        line_ids.append(vals)
            sum_days = 0
            for rec in termination.employee_id.holidays_balance:
                sum_days += rec.holidays_available_stock
            # 2) الإجازة
            if not termination.termination_type_id.all_holidays and sum_days >= termination.termination_type_id.max_days:
                if grid_id:
                    amount = (basic_salary / 22) * termination.termination_type_id.max_days
                    if amount != 0.0:
                        vals = {'difference_id': self.id,
                                'name': 'رصيد إجازة (طي القيد)',
                                'employee_id': termination.employee_id.id,
                                'number_of_days': termination.termination_type_id.max_days,
                                'number_of_hours': 0.0,
                                'amount': amount,
                                'type': 'termination'}
                        line_ids.append(vals)
            if termination.termination_type_id.all_holidays and sum_days > 0:
                if grid_id:
                    amount = (basic_salary / 22) * sum_days
                    if amount != 0.0:
                        vals = {'difference_id': self.id,
                                'name': 'رصيد إجازة (طي القيد)',
                                'employee_id': termination.employee_id.id,
                                'number_of_days': sum_days,
                                'number_of_hours': 0.0,
                                'amount': amount,
                                'type': 'termination'}
                        line_ids.append(vals)
        return line_ids

    @api.multi
    def get_difference_one_third_salary(self):
        self.ensure_one()
        line_ids = []
        difference_history_ids = self.env['hr.payslip.difference.history'].search([('month', '=', fields.Date.from_string(self.date_from).month)])
        for difference_history in difference_history_ids:
            vals = {'difference_id': self.id,
                    'name': 'فرق الحسميات أكثر من ثلث الراتب',
                    'employee_id': difference_history.employee_id.id,
                    'number_of_days': 0.0,
                    'number_of_hours': 0.0,
                    'amount': difference_history.amount,
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
                    'amount': transfert_decision.amount,
                    'type': 'transfert_decision'}
            line_ids.append(vals)
        return line_ids

    @api.multi
    def unlink(self):
        self.ensure_one()
        if self.state != 'new':
            raise ValidationError(u"لا يمكن حذف الفروقات إلا في حالة مسودة أو ملغاه! ")
        return super(HrDifference, self).unlink()


class HrDifferenceLine(models.Model):
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

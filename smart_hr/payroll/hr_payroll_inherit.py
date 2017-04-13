# -*- coding: utf-8 -*-


from openerp import models, fields, api, tools, _
import openerp.addons.decimal_precision as dp
from datetime import datetime
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from openerp.addons.smart_base.util.time_util import days_between
from openerp.addons.smart_base.util.umalqurra import *
from umalqurra.hijri_date import HijriDate
from umalqurra.hijri import Umalqurra
from tempfile import TemporaryFile
import base64
from openerp.exceptions import UserError
from openerp.exceptions import ValidationError


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.multi
    def compute_deductions(self, allowance_total):
        # الحسميات

        line_ids = []
        #  حسم‬  الغياب‬ يكون‬ من‬  جميع البدلات . و  الراتب‬ الأساسي للموظفين‬ الرسميين‬ والمستخدمين
        abscence_ids = self.env['hr.employee.absence.days'].search([('request_id.date', '>=', self.date_from),
                                                                    ('request_id.date', '<=', self.date_to),
                                                                    ('employee_id', '=', self.employee_id.id),
                                                                    ('request_id.state', '=', 'done')
                                                                    ])
        salary_grid, basic_salary = self.employee_id.get_salary_grid_id(False)
        tot_number_request = 0
        for line in abscence_ids:
            amount = (basic_salary + allowance_total) / 30.0 * line.number_request
            vals = {'name': 'غياب بدون عذر',
                    'employee_id': line.employee_id.id,
                    'number_of_days': line.number_request,
                    'number_of_hours': 0.0,
                    'amount': -1 * amount,
                    'category': 'deduction',
                    'type': 'absence'}
            line_ids.append(vals)
            tot_number_request += line.number_request
        # فرق التقاعد: غياب بدون عذر
        if tot_number_request:
            retirement_amount = basic_salary * salary_grid.retirement / 100.0 / 30.0 * tot_number_request
            if retirement_amount != 0:
                vals = {'name': 'فرق التقاعد: غياب بدون عذر',
                        'employee_id': self.employee_id.id,
                        'number_of_days': tot_number_request,
                        'number_of_hours': 0.0,
                        'amount': retirement_amount,
                        'category': 'deduction',
                        'type': 'absence'}
                line_ids.append(vals)

        # حسم‬  التأخير يكون‬ من‬  الراتب‬ الأساسي فقط
        delays_ids = self.env['hr.employee.delay.hours'].search([('request_id.date', '>=', self.date_from),
                                                                 ('request_id.date', '<=', self.date_to),
                                                                 ('request_id.state', '=', 'done')
                                                                 ])
        for line in delays_ids:
            amount = basic_salary / 30.0 * line.number_request
            vals = {'name': 'حسم التأخير والخروج المبكر',
                    'employee_id': line.employee_id.id,
                    'number_of_days': line.number_request,
                    'number_of_hours': 0.0,
                    'amount': -1 * amount,
                    'category': 'deduction',
                    'type': 'retard_leave'}
            line_ids.append(vals)

        # عقوبة
        sanction_line_ids = self.env['hr.sanction.ligne'].search([('sanction_id.date_sanction_start', '>=', self.date_from),
                                                                  ('sanction_id.date_sanction_start', '<=', self.date_to),
                                                                  ('sanction_id.type_sanction.deduction', '=', True),
                                                                  ('sanction_id.state', '=', 'done')
                                                                  ])

        for sanction in sanction_line_ids:
            amount = (basic_salary + allowance_total) / 30.0 * sanction.days_number
            vals = {'name': u'عقوبة',
                    'employee_id': sanction.employee_id.id,
                    'rate': sanction.days_number,
                    'number_of_days': sanction.days_number,
                    'amount': amount * -1,
                    'category': 'deduction',
                    'type': 'sanction',
                    }
            line_ids.append(vals)

        return line_ids

    @api.multi
    def compute_differences(self):
        # احتساب الأثر المالي
        line_ids = []
        # case 1: احتساب الأثر المالي لهذا الشهر
        # فروقات النقل
        # يتم احتساب الأثار المالي للنقل في نفس حالة التعين
        # فروقات التعين
        line_ids += self.get_difference_decision_appoint(self.date_from, self.date_to, self.employee_id, False)
        # فروقات التكليف
        line_ids += self.get_difference_assign(self.date_from, self.date_to, self.employee_id, False)
        # فروقات الإبتعاث
        line_ids += self.get_difference_scholarship(self.date_from, self.date_to, self.employee_id, False)
        # فروقات الإعارة
        line_ids += self.get_difference_lend(self.date_from, self.date_to, self.employee_id, False)
        # فروقات الإجازة
        line_ids += self.get_difference_holidays(self.date_from, self.date_to, self.employee_id, False)
        # فروقات كف اليد
        line_ids += self.get_difference_suspension(self.date_from, self.date_to, self.employee_id, False)
        # فروقات طى القيد
        line_ids += self.get_difference_termination(self.date_from, self.date_to, self.employee_id, False)
        # فرق الحسميات أكثر من ثلث الراتب
        line_ids += self.get_difference_one_third_salary(self.date_from, self.date_to, self.employee_id, False)

        # case 2: احتساب الأثر المالي  لشهر الفارط من تاريخ إعداد مسير الشهر الفرط إلى تاريخ بداية هذا الشهر
        # get last payslip for current employee
        payslip_id = self.env['hr.payslip'].search([('employee_id', '=', self.employee_id.id),
                                                    ('is_special', '=', False),
                                                    ('date_from', '<', self.date_from),
                                                    ('state', '=', 'done')], limit=1, order='date_from desc')
        if payslip_id:
            # add one day to compute_date of last payslip
            compute_date = str(fields.Date.from_string(payslip_id.compute_date) + timedelta(days=1))
            # TODO: review payslip.create_date
            # فروقات النقل
            # فروقات التعين
            line_ids += self.get_difference_decision_appoint(compute_date, payslip_id.date_to, self.employee_id, True)
            # فروقات التكليف
            line_ids += self.get_difference_assign(compute_date, payslip_id.date_to, self.employee_id, True)
            # فروقات الإبتعاث
            line_ids += self.get_difference_scholarship(compute_date, payslip_id.date_to, self.employee_id, True)
            # فروقات الإعارة
            line_ids += self.get_difference_lend(compute_date, payslip_id.date_to, self.employee_id, True)
            # فروقات الإجازة
            line_ids += self.get_difference_holidays(compute_date, payslip_id.date_to, self.employee_id, True)
            # فروقات كف اليد
            line_ids += self.get_difference_suspension(compute_date, payslip_id.date_to, self.employee_id, True)
            # فروقات طى القيد
            line_ids += self.get_difference_termination(compute_date, payslip_id.date_to, self.employee_id, True)
            # فرق الحسميات أكثر من ثلث الراتب
            line_ids += self.get_difference_one_third_salary(compute_date, payslip_id.date_to, self.employee_id, True)
        return line_ids

    @api.multi
    def get_difference_decision_appoint(self, date_from, date_to, employee_id, for_last_month):
        self.ensure_one()
        line_ids = []
        name = ''
        domain = [('is_started', '=', True),
                  ('state_appoint', '=', 'active'),
                  ('date_direct_action', '>=', date_from),
                  ('date_direct_action', '<=', date_to),
                  ('employee_id', '=', employee_id.id)]
        if for_last_month:
            domain.append(('done_date', '>=', date_from))
            domain.append(('done_date', '<=', date_to))
            name = u' للشهر الفارط '
        last_decision_appoint_ids = self.env['hr.decision.appoint'].search(domain, order="date_direct_action desc")
        for decision_appoint in last_decision_appoint_ids:
            for allowance in decision_appoint.decision_apoint_allowance_ids:
                amount = allowance.amount
                vals = {'name': decision_appoint.type_appointment.name + ' : ' + allowance.allowance_id.name + name,
                        'employee_id': decision_appoint.employee_id.id,
                        'number_of_days': 0,
                        'number_of_hours': 0.0,
                        'amount': amount,
                        'type': 'appoint'}
                line_ids.append(vals)
        return line_ids

    @api.multi
    def get_difference_assign(self, date_from, date_to, employee_id, for_last_month):
        self.ensure_one()
        line_ids = []
        name = ''
        domain = [('employee_id', '=', employee_id.id),
                  ('state', '=', 'done')]
        if for_last_month:
            domain.append(('done_date', '>=', date_from))
            domain.append(('done_date', '<=', date_to))
            name = u' للشهر الفارط '
        assign_ids = self.env['hr.employee.commissioning'].search(domain)
        allowance_transport_id = self.env.ref('smart_hr.hr_allowance_type_01')
        for assign_id in assign_ids:
            # overlaped days in current month
            assign_date_from = fields.Date.from_string(assign_id.date_from)
            date_from = fields.Date.from_string(str(date_from))
            assign_date_to = fields.Date.from_string(assign_id.date_to)
            date_to = fields.Date.from_string(str(date_to))
            duration_in_month = 0
            res = {}
            amount_allowance = 0.0
            salary_rate_amount = 0.0
            if date_from >= assign_date_from and assign_date_to > date_to:
                res = self.env['hr.smart.utils'].compute_duration_difference(assign_id.employee_id, date_from, date_to, True, True, True)
            if date_from >= assign_date_from and assign_date_to <= date_to:
                res = self.env['hr.smart.utils'].compute_duration_difference(assign_id.employee_id, date_from, assign_date_to, True, True, True)
            if assign_date_from >= date_from and assign_date_to < date_to:
                res = self.env['hr.smart.utils'].compute_duration_difference(assign_id.employee_id, assign_date_from, assign_date_to, True, True, True)
            if assign_date_from >= date_from and assign_date_to >= date_to:
                res = self.env['hr.smart.utils'].compute_duration_difference(assign_id.employee_id, assign_date_from, date_to, True, True, True)
            if len(res) == 1:
                res = res[0]
                duration_in_month = res['days']
                grid_id = res['grid_id']
                basic_salary = res['basic_salary']
                if assign_id.salary_rate:
                    salary_rate_amount = (duration_in_month * (basic_salary / 30.0) * assign_id.salary_rate / 100.0) * -1
                if assign_id.allowance_transport_rate:
                    allowance_ids = grid_id.allowance_ids
                    for allow in allowance_ids:
                        if allow.allowance_id == allowance_transport_id:
                            amount_allowance = (duration_in_month * (allow.get_value(assign_id.employee_id.id) / 30.0) * assign_id.allowance_transport_rate / 100.0) * -1
                            break
            else:
                for rec in res:
                    grid_id = rec['grid_id']
                    basic_salary = rec['basic_salary']
                    days = rec['days']
                    duration_in_month += days
                    if grid_id and days > 0 and assign_id.salary_rate:
                        rec_amount = ((days * (basic_salary / 30.0) * assign_id.salary_rate) / 100.0) * -1
                        salary_rate_amount += rec_amount
                    if grid_id and days > 0 and assign_id.allowance_transport_rate:
                        allowance_ids = grid_id.allowance_ids
                        for allow in allowance_ids:
                            if allow.allowance_id == allowance_transport_id:
                                amount_allowance += (days * (allow.get_value(assign_id.employee_id.id) / 30.0) * assign_id.allowance_transport_rate / 100.0) * -1
                                break

            # 1 الراتب
            if salary_rate_amount < 0:
                vals = {'name': ' فرق الراتب التي توفرها الجهة: تكليف' + name,
                        'employee_id': assign_id.employee_id.id,
                        'number_of_days': duration_in_month,
                        'number_of_hours': 0.0,
                        'amount': salary_rate_amount,
                        'type': 'commissioning'}
                line_ids.append(vals)
            if amount_allowance < 0:
                vals = {'name': 'فرق بدل النقل الذي توفره الجهة: تكليف' + name,
                        'employee_id': assign_id.employee_id.id,
                        'number_of_days': duration_in_month,
                        'number_of_hours': 0.0,
                        'amount': amount_allowance,
                        'type': 'commissioning'}
                line_ids.append(vals)
        return line_ids

    @api.multi
    def get_difference_scholarship(self, date_from, date_to, employee_id, for_last_month):
        self.ensure_one()
        line_ids = []
        name = ''
        domain = [('employee_id', '=', employee_id.id),
                  ('state', '=', 'done')
                  ]
        if for_last_month:
            domain.append(('done_date', '>=', date_from))
            domain.append(('done_date', '<=', date_to))
            name = u' للشهر الفارط '
        scholarship_ids = self.env['hr.scholarship'].search(domain)
        final_retirement_amount = 0.0
        allow_exception_amount = 0.0
        for scholarship_id in scholarship_ids:
            # overlaped days in current month
            scholarship_date_from = fields.Date.from_string(scholarship_id.date_from)
            date_from = fields.Date.from_string(date_from)
            scholarship_date_to = fields.Date.from_string(scholarship_id.date_to)
            date_to = fields.Date.from_string(date_to)
            duration_in_month = 0
            retirement_amount = 0.0
            res = {}
            if date_from >= scholarship_date_from and scholarship_date_to > date_to:
                res = self.env['hr.smart.utils'].compute_duration_difference(scholarship_id.employee_id, date_from, date_to, True, True, True)
            if date_from >= scholarship_date_from and scholarship_date_to <= date_to:
                res = self.env['hr.smart.utils'].compute_duration_difference(scholarship_id.employee_id, date_from, scholarship_date_to, True, True, True)
            if scholarship_date_from >= date_from and scholarship_date_to < date_to:
                res = self.env['hr.smart.utils'].compute_duration_difference(scholarship_id.employee_id, scholarship_date_from, scholarship_date_to, True, True, True)
            if scholarship_date_from >= date_from and scholarship_date_to >= date_to:
                res = self.env['hr.smart.utils'].compute_duration_difference(scholarship_id.employee_id, scholarship_date_from, date_to, True, True, True)
            if len(res) == 1:
                res = res[0]
                duration_in_month = res['days']
                grid_id = res['grid_id']
                basic_salary = res['basic_salary']
                retirement_amount = duration_in_month * basic_salary / 30.0 * grid_id.retirement / 100.0
                basic_salary_after_retirement = duration_in_month * basic_salary / 30.0 - retirement_amount
                final_retirement_amount += basic_salary_after_retirement - ((basic_salary_after_retirement * scholarship_id.scholarship_type.salary_percent) / 100.0)
                final_retirement_amount *= -1
                # البدلات المستثناة
                alowances_in_grid_id = [rec.allowance_id for rec in grid_id.allowance_ids]
                for allowance in scholarship_id.scholarship_type.hr_allowance_type_id:
                    # check if the allowance in employe's salary_grade_id
                    if allowance in alowances_in_grid_id:
                        for allow in grid_id.allowance_ids:
                            if allow.allowance_id == allowance:
                                allow_exception_amount = allow.get_value(scholarship_id.employee_id.id)
                                break
                allow_exception_amount *= -1
            else:
                for rec in res:
                    grid_id = rec['grid_id']
                    days = rec['days']
                    duration_in_month += days
                    retirement_amount = days * basic_salary / 30.0 * grid_id.retirement / 100.0
                    basic_salary_after_retirement = days * basic_salary / 30.0 - retirement_amount
                    final_retirement_amount += basic_salary_after_retirement - ((basic_salary_after_retirement * scholarship_id.scholarship_type.salary_percent) / 100.0)
                    # البدلات المستثناة
                    alowances_in_grid_id = [allow.allowance_id for allow in grid_id.allowance_ids]
                    for allowance in scholarship_id.scholarship_type.hr_allowance_type_id:
                        # check if the allowance in employe's salary_grade_id
                        if allowance in alowances_in_grid_id:
                            for allow in grid_id.allowance_ids:
                                if allow.allowance_id == allowance:
                                    allow_exception_amount += days * allow.get_value(scholarship_id.employee_id.id) / 100.0
                                    break
                final_retirement_amount *= -1
            # 1) البدلات المستثناة
            if allow_exception_amount < 0:
                vals = {'name': '' + allowance.name + name,
                        'employee_id': scholarship_id.employee_id.id,
                        'number_of_days': duration_in_month,
                        'number_of_hours': 0.0,
                        'amount': allow_exception_amount,
                        'type': 'scholarship'}
                line_ids.append(vals)
            # 2) نسبة الراتب بعد حسم التقاعد
            if final_retirement_amount < 0:
                vals = {'name': u'نسبة الراتب بعد حسم التقاعد' + name,
                        'employee_id': scholarship_id.employee_id.id,
                        'number_of_days': duration_in_month,
                        'number_of_hours': 0.0,
                        'amount': final_retirement_amount,
                        'type': 'scholarship'}
                line_ids.append(vals)
        return line_ids

    @api.multi
    def get_difference_lend(self, date_from, date_to, employee_id, for_last_month):
        self.ensure_one()
        line_ids = []
        name = ''
        domain = [('state', '=', 'done'),
                  ('employee_id', '=', employee_id.id),
                  ]
        if for_last_month:
            domain.append(('done_date', '>=', date_from))
            domain.append(('done_date', '<=', date_to))
            name = u' للشهر الفارط '
        lend_ids = self.env['hr.employee.lend'].search(domain)
        amount_retirement = 0.0
        allowance_amount = 0.0
        amount = 0.0
        for lend_id in lend_ids:
            # overlaped days in current month
            lend_date_from = fields.Date.from_string(lend_id.date_from)
            date_from = fields.Date.from_string(date_from)
            lend_date_to = fields.Date.from_string(lend_id.date_to)
            date_to = fields.Date.from_string(date_to)
            duration_in_month = 0
            res = []
            if date_from >= lend_date_from and lend_date_to > date_to:
                res = self.env['hr.smart.utils'].compute_duration_difference(lend_id.employee_id, date_from, date_to, True, False, False)
            if date_from >= lend_date_from and lend_date_to <= date_to:
                res = self.env['hr.smart.utils'].compute_duration_difference(lend_id.employee_id, date_from, lend_date_to, True, False, False)
            if lend_date_from >= date_from and lend_date_to < date_to:
                res = self.env['hr.smart.utils'].compute_duration_difference(lend_id.employee_id, lend_date_from, lend_date_to, True, False, False)
            if lend_date_from >= date_from and lend_date_to >= date_to:
                res = self.env['hr.smart.utils'].compute_duration_difference(lend_id.employee_id, lend_date_from, date_to, True, False, False)

            hr_setting = self.env['hr.setting'].search([], limit=1)
            employee_allowances = lend_id.employee_id.hr_employee_allowance_ids
            if len(res) == 1:
                res = res[0]
                duration_in_month = res['days']
                grid_id = res['grid_id']
                basic_salary = res['basic_salary']
                amount = ((duration_in_month * (basic_salary / 30.0) * lend_id.salary_proportion) / 100.0) * -1
                if hr_setting and lend_id.pay_retirement:
                    amount_retirement = (duration_in_month * basic_salary / 30.0 * hr_setting.retirement_proportion) / 100.0
                # البدلات
                employee_allowances = lend_id.employee_id.hr_employee_allowance_ids
                for allowance in lend_id.allowance_ids:
                    for rec in employee_allowances:
                        if rec.salary_grid_detail_id == grid_id and allowance.allowance_id == rec.allowance_id:
                            if allowance.amount < rec.amount:
                                allowance_amount += duration_in_month * allowance.amount / 30.0
                            if allowance.amount >= rec.amount:
                                allowance_amount += duration_in_month * rec.amount / 30.0
                allowance_amount *= -1
            else:
                for rec in res:
                    grid_id = rec['grid_id']
                    basic_salary = rec['basic_salary']
                    days = rec['days']
                    if grid_id and days > 0:
                        rec_amount = ((days * (basic_salary / 30.0) * lend_id.salary_proportion) / 100.0) * -1
                        duration_in_month += days
                        amount += rec_amount
                        if hr_setting and lend_id.pay_retirement:
                            amount_retirement += (days * (basic_salary / 30.0) * hr_setting.retirement_proportion / 100.0) * -1
                        # البدلات
                        for allowance in lend_id.allowance_ids:
                            for rec in employee_allowances:
                                if rec.salary_grid_detail_id == grid_id and allowance.allowance_id == rec.allowance_id:
                                    if allowance.amount < rec.amount:
                                        allowance_amount += days * allowance.amount / 30.0
                                    if allowance.amount >= rec.amount:
                                        allowance_amount += days * rec.amount / 30.0
                        allowance_amount *= -1
            # 1 الراتب
            if amount < 0:
                vals = {'name': 'الإعارة نسبة الراتب' + name,
                        'employee_id': lend_id.employee_id.id,
                        'number_of_days': duration_in_month,
                        'number_of_hours': 0.0,
                        'amount': amount,
                        'type': 'lend'
                        }
                line_ids.append(vals)

            # 2 -البدلات
            if allowance_amount < 0:
                vals = {'name': 'فرق البدلات التي تتحملها الجهة: إعارة' + name,
                        'employee_id': lend_id.employee_id.id,
                        'number_of_days': duration_in_month,
                        'number_of_hours': 0.0,
                        'amount': allowance_amount,
                        'type': 'lend'
                        }
                line_ids.append(vals)
            # 3) حصة الحكومة من التقاعد
            if amount_retirement:
                vals = {'name': 'حصة الحكومة من التقاعد: الإعارة' + name,
                        'employee_id': lend_id.employee_id.id,
                        'number_of_days': duration_in_month,
                        'number_of_hours': 0.0,
                        'amount': amount_retirement,
                        'type': 'lend'}
                line_ids.append(vals)

        return line_ids

    @api.multi
    def get_difference_holidays(self, date_from, date_to, employee_id, for_last_month):
        self.ensure_one()
        line_ids = []
        name = ''
        domain = [('employee_id', '=', employee_id.id),
                  ('state', '=', 'done')]
        if for_last_month:
            domain.append(('done_date', '>=', date_from))
            domain.append(('done_date', '<=', date_to))
            name = u' للشهر الفارط '
        holidays_ids = self.env['hr.holidays'].search(domain)
        holiday_status_maternity = self.env.ref('smart_hr.data_hr_holiday_status_maternity')
        for holiday_id in holidays_ids:
            holiday_status_id = holiday_id.holiday_status_id
            # get the entitlement type
            if not holiday_id.entitlement_type:
                entitlement_type = self.env.ref('smart_hr.data_hr_holiday_entitlement_all')
            else:
                entitlement_type = holiday_id.entitlement_type
            # overlaped days in current month
            holiday_date_from = fields.Date.from_string(holiday_id.date_from)
            date_from = fields.Date.from_string(str(date_from))
            holiday_date_to = fields.Date.from_string(str(holiday_id.date_to))
            date_to = fields.Date.from_string(str(date_to))
            duration_in_month = 0
            res = []
            if date_from >= holiday_date_from and holiday_date_to > date_to:
                res = self.env['hr.smart.utils'].compute_duration_difference(holiday_id.employee_id, date_from, date_to, True, True, True)
            if date_from >= holiday_date_from and holiday_date_to <= date_to:
                res = self.env['hr.smart.utils'].compute_duration_difference(holiday_id.employee_id, date_from, holiday_date_to, True, True, True)
            if holiday_date_from >= date_from and holiday_date_to < date_to:
                res = self.env['hr.smart.utils'].compute_duration_difference(holiday_id.employee_id, holiday_date_from, holiday_date_to, True, True, True)
            if holiday_date_from >= date_from and holiday_date_to >= date_to:
                res = self.env['hr.smart.utils'].compute_duration_difference(holiday_id.employee_id, holiday_date_from, date_to, True, True, True)
            basic_salary_amount = 0.0
            basic_salary_amount2 = 0.0
            retirement_amount = 0.0
            retirement_amount2 = 0.0
            allowance_amount = 0.0
            allowance_amount2 = 0.0
            if len(res) == 1:
                res = res[0]
                grid_id = res['grid_id']
                basic_salary = res['basic_salary']
                duration_in_month = res['days']
                # فرق الراتب الأساسي
                if not holiday_status_id.salary_spending:
                    basic_salary_amount = (duration_in_month * (basic_salary / 30.0))
                    # فرق البدلات
                    allowance_amount = 0.0
                    if duration_in_month > 0:
                        for allowance in holiday_id.employee_id.get_employee_allowances(grid_id.date):
                            allowance_amount += allowance['amount'] / 30.0 * duration_in_month
                            if holiday_status_id.transport_allowance and allowance['allowance_id'] == self.env.ref('smart_hr.hr_allowance_type_01').id:
                                allowance_amount -= allowance['amount'] / 30.0 * duration_in_month
                # فرق التقاعد
                if holiday_status_id.deductible_duration_service:
                    retirement_amount = basic_salary * grid_id.retirement / 100.0 / 30.0 * duration_in_month
                # case of  لا يصرف له راتب كامل
                if grid_id and holiday_status_id.salary_spending and holiday_status_id.percentages:
                    for rec in holiday_status_id.percentages:
                        today = fields.Date.from_string(fields.Date.today())
                        if rec.entitlement_id.periode:
                            get_from_date = today - relativedelta(years=rec.entitlement_id.periode)
                            # get first token holiday with same type
                            oldest_holiday_id = self.env['hr.holidays'].search([('holiday_status_id', '=', holiday_status_id.id),
                                                                                ('employee_id', '=', holiday_id.employee_id.id),
                                                                                ('state', '=', 'done'),
                                                                                ('date_from', '>=', get_from_date),
                                                                                ], order='done_date asc', limit=1)
                            months_from_holiday_start = relativedelta(today, fields.Date.from_string(oldest_holiday_id.date_from)).months
                        if entitlement_type == rec.entitlement_id.entitlment_category and rec.month_from <= months_from_holiday_start <= rec.month_to and duration_in_month > 0:
                            basic_salary_amount = (duration_in_month * (basic_salary / 30.0) * (100 - rec.salary_proportion)) / 100.0
                            if holiday_status_maternity == holiday_status_id:
                                ret_amount = basic_salary * grid_id.retirement / 100.0
                                basic_salary_amount = ((basic_salary - ret_amount) * (100 - rec.salary_proportion)) / 100.0
                                diff = holiday_status_maternity.min_amount - (((basic_salary - ret_amount)) * (rec.salary_proportion)) / 100.0
                                if diff > 0:
                                    basic_salary_amount -= diff
                                # amout depend of number of days
                                basic_salary_amount = basic_salary_amount * duration_in_month / 30.0
                            # فرق البدلات
                            allowance_amount2 = 0.0
                            if holiday_status_id.transport_allowance and allowance['allowance_id'] == self.env.ref('smart_hr.hr_allowance_type_01').id:
                                allowance_amount2 -= allowance['amount'] / 30.0 * duration_in_month
                                if duration_in_month > 0 and allowance_amount2 != 0:
                                    vals = {'name': 'فرق بدلات : ' + holiday_id.holiday_status_id.name + name,
                                            'employee_id': holiday_id.employee_id.id,
                                            'number_of_days': duration_in_month,
                                            'number_of_hours': 0.0,
                                            'amount': allowance_amount2 * -1,
                                            'type': 'holiday'}
                                    line_ids.append(vals)
            else:
                for rec in res:
                    grid_id = rec['grid_id']
                    basic_salary = rec['basic_salary']
                    days = rec['days']
                    duration_in_month += days
                    # فرق الراتب الأساسي
                    if not holiday_status_id.salary_spending:
                        basic_salary_amount += (days * (basic_salary / 30.0))
                        # فرق البدلات
                        allowance_amount = 0.0
                        if days > 0:
                            for allowance in holiday_id.employee_id.get_employee_allowances(grid_id.date):
                                allowance_amount += allowance['amount'] / 30.0 * days
                                if holiday_status_id.transport_allowance and allowance['allowance_id'] == self.env.ref('smart_hr.hr_allowance_type_01').id:
                                    allowance_amount -= allowance['amount'] / 30.0 * days
                    # فرق التقاعد
                    if holiday_status_id.deductible_duration_service:
                        retirement_amount += basic_salary * grid_id.retirement / 100.0 / 30.0 * days
                    # case of  لا يصرف له راتب كامل
                    if grid_id and holiday_status_id.salary_spending and holiday_status_id.percentages:
                        for rec in holiday_status_id.percentages:
                            today = fields.Date.from_string(fields.Date.today())
                            if rec.entitlement_id.periode:
                                get_from_date = today - relativedelta(years=rec.entitlement_id.periode)
                                # get first token holiday with same type
                                oldest_holiday_id = self.env['hr.holidays'].search([('holiday_status_id', '=', holiday_status_id.id),
                                                                                    ('employee_id', '=', holiday_id.employee_id.id),
                                                                                    ('state', '=', 'done'),
                                                                                    ('date_from', '>=', get_from_date),
                                                                                    ], order='done_date asc', limit=1)
                                months_from_holiday_start = relativedelta(today, fields.Date.from_string(oldest_holiday_id.date_from)).months
                            if entitlement_type == rec.entitlement_id.entitlment_category and rec.month_from <= months_from_holiday_start <= rec.month_to and days > 0:
                                basic_salary_amount2 += (days * (basic_salary / 30.0) * (100 - rec.salary_proportion)) / 100.0
                                if holiday_status_maternity == holiday_status_id:
                                    ret_amount = basic_salary * grid_id.retirement / 100.0
                                    basic_salary_amount2 += ((basic_salary - ret_amount) * (100 - rec.salary_proportion)) / 100.0
                                    diff = holiday_status_maternity.min_amount - (((basic_salary - ret_amount)) * (rec.salary_proportion)) / 100.0
                                    if diff > 0:
                                        basic_salary_amount2 -= diff
                                    # amout depend of number of days
                                    basic_salary_amount2 += basic_salary_amount2 * days / 30.0
                            # فرق البدلات
                            allowance_amount2 = 0.0
                            if holiday_status_id.transport_allowance and allowance['allowance_id'] == self.env.ref('smart_hr.hr_allowance_type_01').id:
                                allowance_amount2 -= allowance['amount'] / 30.0 * days
                            # فرق التقاعد
                            if holiday_status_id.deductible_duration_service:
                                retirement_amount2 += (basic_salary * grid_id.retirement / 100.0 * (100 - rec.salary_proportion) / 100.0) / 30.0 * days
            # case of لا يصرف له الراتب
            if basic_salary_amount:
                vals = {'name': holiday_id.holiday_status_id.name + name,
                        'employee_id': holiday_id.employee_id.id,
                        'number_of_days': duration_in_month,
                        'number_of_hours': 0.0,
                        'amount': basic_salary_amount * -1,
                        'type': 'holiday'}
                line_ids.append(vals)

            if allowance_amount:
                vals = {'name': 'فرق بدلات ' + holiday_id.holiday_status_id.name + name,
                        'employee_id': holiday_id.employee_id.id,
                        'number_of_days': duration_in_month,
                        'number_of_hours': 0.0,
                        'amount': allowance_amount * -1,
                        'type': 'holiday'}
                line_ids.append(vals)
            # فرق التقاعد
            if retirement_amount != 0:
                vals = {'name': 'فرق التقاعد‬ ' + holiday_id.holiday_status_id.name + name,
                        'employee_id': holiday_id.employee_id.id,
                        'number_of_days': duration_in_month,
                        'number_of_hours': 0.0,
                        'amount': retirement_amount,
                        'type': 'holiday'}
                line_ids.append(vals)
            # case with percentages
            if basic_salary_amount2:
                vals = {'name': holiday_id.holiday_status_id.name + name,
                        'employee_id': holiday_id.employee_id.id,
                        'number_of_days': duration_in_month,
                        'number_of_hours': 0.0,
                        'amount': basic_salary_amount2 * -1,
                        'type': 'holiday'}
                line_ids.append(vals)
            # فرق البدلات
            if allowance_amount2:
                vals = {'name': 'فرق بدلات : ' + holiday_id.holiday_status_id.name + name,
                        'employee_id': holiday_id.employee_id.id,
                        'number_of_days': duration_in_month,
                        'number_of_hours': 0.0,
                        'amount': allowance_amount2 * -1,
                        'type': 'holiday'}
                line_ids.append(vals)
            # فرق التقاعد
            if retirement_amount2:
                vals = {'name': 'فرق التقاعد‬ : ' + holiday_id.holiday_status_id.name + name,
                        'employee_id': holiday_id.employee_id.id,
                        'number_of_days': duration_in_month,
                        'number_of_hours': 0.0,
                        'amount': retirement_amount2,
                        'type': 'holiday'}
                line_ids.append(vals)
            # case of  نوع التعويض    مقابل ‫مادي‬ ‬   اجازة التعويض
            grid_id, basic_salary = employee_id.get_salary_grid_id(False)
            if grid_id:
                if holiday_id.compensation_type and holiday_id.compensation_type == 'money':
                    amount = (holiday_id.token_compensation_stock * (basic_salary / 30.0))
                    if amount != 0:
                        vals = {'name': holiday_id.holiday_status_id.name + u"(تعويض مالي)" + name,
                                'employee_id': holiday_id.employee_id.id,
                                'number_of_days': int(holiday_id.current_holiday_stock),
                                'number_of_hours': 0.0,
                                'amount': amount,
                                'type': 'holiday'}
                        line_ids.append(vals)
        return line_ids

    @api.multi
    def get_difference_suspension(self, date_from, date_to, employee_id, for_last_month):
        # # إذا كان كف اليد على كامل الشهر الحالي فيجب احتساب الفرق على أساس  30 يوم   وإلا فيحتسب على عدد أيام الكف.
        # إذا كان عدد أيام الشهر أصغر من 30 يتم احتساب قيمة أيام فرق  مساوي إلى قيمة أخر يوم في الشهر.
        # مثلا شهر فيه 28 يوم يكون  قيمة يوم 29 و-30 مساوي لقيمة يوم 28.

        date_start_month = str(self.period_id.date_start)
        date_end_month = str(self.period_id.date_stop)
        date_from_param = date_from
        date_to_param = date_to

        def _all_days_in_month(date_from, date_to):
            if date_start_month >= date_from and date_end_month <= date_to:
                return True
            return False

        self.ensure_one()
        line_ids = []
        all_suspensions = []
        # get  started and ended condemned suspension in current month
        domain = [('suspension_date', '>=', date_from),
                  ('suspension_date', '<=', date_to),
                  ('state', '=', 'done'),
                  ('suspension_end_id.release_date', '>=', date_from),
                  ('suspension_end_id.release_date', '<=', date_to),
                  ('suspension_end_id.condemned', '=', True),
                  ('employee_id', '=', employee_id.id),
                  ('suspension_end_id.state', '=', 'done'),
                  ]
        name = ''
        if for_last_month:
            domain.append(('done_date', '>=', date_from))
            domain.append(('done_date', '<=', date_to))
            name = u' للشهر الفارط '
        suspension_ids = self.env['hr.suspension'].search(domain)
        for suspension in suspension_ids:
            date_from = suspension.suspension_date
            date_to = suspension.suspension_end_id.release_date
            if date_from < date_from:
                date_from = date_from
            if date_to > date_to:
                date_to = date_to
            number_of_days = days_between(date_from, date_to)
            if number_of_days > 0 and suspension.suspension_end_id.condemned:
                all_suspensions.append({'employee_id': suspension.employee_id.id,
                                        'date_from': date_from, 'date_to': date_to,
                                        'number_of_days': number_of_days, 'return': False})

        # get started suspension in this month and not ended in current month or dont have yet an end
        domain = [('suspension_date', '>=', date_from),
                  ('suspension_date', '<=', date_to),
                  ('state', '=', 'done'),
                  ('employee_id', '=', employee_id.id),
                  ('suspension_end_id', '=', False)
                  ]
        if for_last_month:
            domain.append(('done_date', '>=', date_from))
            domain.append(('done_date', '<=', date_to))
            name = u' للشهر الفارط '
        suspension_ids = self.env['hr.suspension'].search(domain)
        domain = [('suspension_date', '>=', date_from),
                  ('suspension_date', '<=', date_to),
                  ('state', '=', 'done'),
                  ('employee_id', '=', employee_id.id),
                  ('suspension_end_id.release_date', '>', date_to),
                  ('suspension_end_id.state', '=', 'done'),
                  ]
        if for_last_month:
            domain.append(('done_date', '>=', date_from))
            domain.append(('done_date', '<=', date_to))
            name = u' للشهر الفارط '
        suspension_ids += self.env['hr.suspension'].search(domain)
        for suspension in suspension_ids:
            date_from = suspension.suspension_date
            date_to = date_to
            number_of_days = days_between(date_from, date_to)
            if number_of_days > 0:
                all_suspensions.append({'employee_id': suspension.employee_id.id,
                                        'date_from': date_from, 'date_to': date_to,
                                        'number_of_days': number_of_days, 'return': False})
        # get started suspension before this month and not yet ended
        domain = [('suspension_date', '<', date_from),
                  ('state', '=', 'done'),
                  ('employee_id', '=', employee_id.id),
                  ('suspension_end_id', '=', False)
                  ]
        if for_last_month:
            domain.append(('done_date', '>=', date_from))
            domain.append(('done_date', '<=', date_to))
            name = u' للشهر الفارط '
        suspension_ids = self.env['hr.suspension'].search(domain)
        domain = [('suspension_date', '<', date_from),
                  ('state', '=', 'done'),
                  ('employee_id', '=', employee_id.id),
                  ('suspension_end_id.release_date', '>', date_to),
                  ('suspension_end_id.state', '=', 'done'),
                  ]
        if for_last_month:
            domain.append(('done_date', '>=', date_from))
            domain.append(('done_date', '<=', date_to))
            name = u' للشهر الفارط '
        suspension_ids += self.env['hr.suspension'].search(domain)
        for suspension in suspension_ids:
            date_from = date_from
            date_to = date_to
            number_of_days = days_between(date_from, date_to)
            if number_of_days > 0:
                all_suspensions.append({'employee_id': suspension.employee_id.id,
                                        'date_from': date_from, 'date_to': date_to,
                                        'number_of_days': number_of_days, 'return': False})
        # get started suspension before this month and ended in current month
        domain = [('suspension_date', '<', date_from),
                  ('state', '=', 'done'),
                  ('employee_id', '=', employee_id.id),
                  ('suspension_end_id.release_date', '>=', date_from),
                  ('suspension_end_id.release_date', '<=', date_to),
                  ('suspension_end_id.state', '=', 'done'),
                  ]
        if for_last_month:
            domain.append(('done_date', '>=', date_from))
            domain.append(('done_date', '<=', date_to))
            name = u' للشهر الفارط '
        suspension_ids = self.env['hr.suspension'].search(domain)
        for suspension in suspension_ids:
            # case 1: condemned
            if suspension.suspension_end_id.condemned:
                date_from = date_from
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
            # 1- الراتب الأساسي : احتساب نصف الراتب الأساسي
            # must browse interval date from, date to to get the correct basic_salary for each date
            # overlaped days in current month
            suspension_date_from = fields.Date.from_string(suspension['date_from'])
            date_from = fields.Date.from_string(str(date_from_param))
            suspension_date_to = fields.Date.from_string(suspension['date_to'])
            date_to = fields.Date.from_string(str(date_to_param))
            duration_in_month = 0
            res = []
            if date_from >= suspension_date_from and suspension_date_to > date_to:
                print 'hello1'
                res = self.env['hr.smart.utils'].compute_duration_difference(employee, date_from, date_to, True, True, True)
            if date_from >= suspension_date_from and suspension_date_to <= date_to:
                print 'hello2'
                res = self.env['hr.smart.utils'].compute_duration_difference(employee, date_from, suspension_date_to, True, True, True)
            if suspension_date_from >= date_from and suspension_date_to < date_to:
                print 'hello3'
                res = self.env['hr.smart.utils'].compute_duration_difference(employee, suspension_date_from, suspension_date_to, True, True, True)
            if suspension_date_from >= date_from and suspension_date_to >= date_to:
                print 'hello4'
                res = self.env['hr.smart.utils'].compute_duration_difference(employee, suspension_date_from, date_to, True, True, True)
            amount = 0.0
            retirement_amount = 0.0
            allowance_amount = 0.0
            multiplication = -1.0
            number_of_days = 0.0
            if suspension['return']:
                multiplication = 1.0
            if len(res) == 1:
                res = res[0]
                grid_id = res['grid_id']
                basic_salary = res['basic_salary']
                duration_in_month = res['days']
                # فرق الراتب الأساسي كف اليد
                retirement_amount = basic_salary * grid_id.retirement / 100.0 / 30.0 * duration_in_month
                amount = ((basic_salary / 30.0) * duration_in_month - retirement_amount) / 2.0
                # 2- البدلات لا تحتسب في حال كان الموظف مكفوف اليد
                for allowance in grid_id.allowance_ids:
                    allowance_val = allowance.get_value(employee.id) / 30.0
                    allowance_amount += allowance_val
                allowance_amount *= duration_in_month
            else:
                for rec in res:
                    grid_id = rec['grid_id']
                    basic_salary = rec['basic_salary']
                    days = rec['days']
                    duration_in_month += days
                    # فرق الراتب الأساسي كف اليد
                    retirement_amount = basic_salary * grid_id.retirement / 100.0 / 30.0 * days
                    amount += ((basic_salary / 30.0) * days - retirement_amount) / 2.0
                    # 2- البدلات لا تحتسب في حال كان الموظف مكفوف اليد
                    for allowance in grid_id.allowance_ids:
                        allowance_val = allowance.get_value(employee.id) / 30.0
                        allowance_amount += allowance_val * days
            # فرق الراتب الأساسي كف اليد
            if amount:
                val = {'name': 'فرق الراتب الأساسي كف اليد' + name,
                       'employee_id': employee.id,
                       'number_of_days': duration_in_month,
                       'number_of_hours': 0.0,
                       'amount': amount * multiplication,
                       'type': 'suspension'}
                line_ids.append(val)
            # 2- البدلات لا تحتسب في حال كان الموظف مكفوف اليد
            if allowance_amount:
                val = {'name': ' فرق البدلات كف اليد' + name,
                       'employee_id': employee.id,
                       'number_of_days': duration_in_month,
                       'number_of_hours': 0.0,
                       'amount': allowance_amount * multiplication,
                       'type': 'suspension'}
                line_ids.append(val)

        return line_ids

    @api.multi
    def get_difference_termination(self, date_from, date_to, employee_id, for_last_month):
        self.ensure_one()
        line_ids = []
        domain = [('date', '>=', date_from),
                  ('date', '<=', date_to),
                  ('employee_id', '=', employee_id.id),
                  ('state', '=', 'done')
                  ]
        name = ''
        if for_last_month:
            domain.append(('done_date', '>=', date_from))
            domain.append(('done_date', '<=', date_to))
            name = u' للشهر الفارط '
        termination_ids = self.env['hr.termination'].search(domain)
        for termination in termination_ids:
            grid_id, basic_salary = termination.employee_id.get_salary_grid_id(termination.date)
            if grid_id:
                # فرق الأيام المخصومة من الشهر
                date_from = date_from
                date_to = termination.date_termination
                worked_days = days_between(date_from, date_to) - 1
                unworked_days = 30.0 - worked_days
                if unworked_days > 0:
                    amount = (basic_salary / 30.0) * unworked_days
                    vals = {'name': termination.termination_type_id.name + " " + u'(فرق الأيام المخصومة من الشهر)' + name,
                            'employee_id': termination.employee_id.id,
                            'number_of_days': unworked_days,
                            'number_of_hours': 0.0,
                            'amount': amount * -1,
                            'type': 'termination'}
                    line_ids.append(vals)
            # سعودي
            if termination.employee_id.country_id and termination.employee_id.country_id.code_nat == 'SA':
                if grid_id:
                    # 1) عدد الرواتب المستحق
                    if termination.termination_type_id.nb_salaire > 0:
                        amount = basic_salary * (termination.termination_type_id.nb_salaire - 1)
                        vals = {'name': termination.termination_type_id.name + " " + u'(عدد الرواتب)' + name,
                                'employee_id': termination.employee_id.id,
                                'number_of_days': (termination.termination_type_id.nb_salaire - 1) * 30.0,
                                'number_of_hours': 0.0,
                                'amount': amount,
                                'type': 'termination'}
                        line_ids.append(vals)
            sum_days = 0
            for rec in termination.employee_id.holidays_balance:
                sum_days += rec.holidays_available_stock
            # 2) الإجازة
            if sum_days >= termination.termination_type_id.max_days:
                sum_days = termination.termination_type_id.max_days
            if termination.termination_type_id.all_holidays and sum_days > 0:
                if grid_id:
                    amount = (basic_salary / 30.0) * sum_days
                    if amount != 0.0:
                        vals = {'name': 'رصيد إجازة (طي القيد)' + name,
                                'employee_id': termination.employee_id.id,
                                'number_of_days': sum_days,
                                'number_of_hours': 0.0,
                                'amount': amount,
                                'type': 'termination'}
                        line_ids.append(vals)
        return line_ids

    @api.multi
    def get_difference_one_third_salary(self, date_from, date_to, employee_id, for_last_month):
        self.ensure_one()
        line_ids = []
        domain = [('month', '=', fields.Date.from_string(date_from).month),
                  ('employee_id', '=', employee_id.id),
                  ]
        name = ''
        if for_last_month:
            domain.append(('done_date', '>=', date_from))
            domain.append(('done_date', '<=', date_to))
            name = u' للشهر الفارط '
        difference_history_ids = self.env['hr.payslip.difference.history'].search(domain)
        for difference_history in difference_history_ids:
            vals = {'name': 'فرق الحسميات أكثر من ثلث الراتب' + name,
                    'employee_id': difference_history.employee_id.id,
                    'number_of_days': 0.0,
                    'number_of_hours': 0.0,
                    'amount': difference_history.amount,
                    'type': 'one_third_salary'}
            line_ids.append(vals)
        return line_ids

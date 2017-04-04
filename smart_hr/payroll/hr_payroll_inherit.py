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
                                                                    ('request_id.state', '=', 'done')
                                                                    ])
        salary_grid, basic_salary = self.employee_id.get_salary_grid_id(False)
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
                    'amount': amount,
                    'category': 'deduction',
                    'type': 'sanction',
                    }
            line_ids.append(vals)

        return line_ids

    @api.multi
    def compute_differences(self):
        # احتساب الأثر المالي
        line_ids = []
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
        return line_ids

    @api.multi
    def get_difference_transfert(self):
        self.ensure_one()
        line_ids = []
        hr_setting = self.env['hr.setting'].search([], limit=1)
        if hr_setting:
            transfert_ids = self.env['hr.employee.transfert'].search([('create_date', '>=', self.date_from),
                                                                      ('create_date', '<=', self.date_to),
                                                                      ('employee_id', '=', self.employee_id.id),
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
                                                                            ('employee_id', '=', self.employee_id.id),
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
                                                                   ('employee_id', '=', self.employee_id.id),
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
                                                             ('employee_id', '=', self.employee_id.id),
                                                             ('state', '=', 'done')
                                                             ])
        for scholarship_id in scholarship_ids:
            grid_id, basic_salary = scholarship_id.employee_id.get_salary_grid_id(scholarship_id.date_to)
            if grid_id:
                # 1) البدلات المستثناة
                alowances_in_grade_id = [rec.allowance_id for rec in grid_id.allowance_ids]
                for allowance in scholarship_id.scholarship_type.hr_allowance_type_id:
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
                # 2) نسبة الراتب بعد حسم التقاعد
                retirement_amount = basic_salary * grid_id.retirement / 100.0
                basic_salary_after_retirement = basic_salary - retirement_amount
                amount = basic_salary_after_retirement - ((basic_salary_after_retirement * scholarship_id.scholarship_type.salary_percent) / 100.0)
                if amount > 0:
                    vals = {'difference_id': self.id,
                            'name': u'نسبة الراتب بعد حسم التقاعد',
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
        lend_ids = self.env['hr.employee.lend'].search([('state', '=', 'done'),
                                                        ('employee_id', '=', self.employee_id.id),
                                                        ])
        for lend_id in lend_ids:
            # overlaped days in current month
            lend_date_from = fields.Date.from_string(lend_id.date_from)
            date_from = fields.Date.from_string(self.date_from)
            lend_date_to = fields.Date.from_string(lend_id.date_to)
            date_to = fields.Date.from_string(self.date_to)
            duration_in_month = 0
            if date_from >= lend_date_from and lend_date_to >= date_to:
                res = self.env['hr.smart.utils'].compute_duration_difference(lend_id.employee_id, date_from, date_to, True, True, True)
            if lend_date_from >= date_from and lend_date_to <= date_to:
                res = self.env['hr.smart.utils'].compute_duration_difference(lend_id.employee_id, lend_date_to, lend_date_from, True, True, True)
            if lend_date_from >= date_from and lend_date_to >= date_to:
                res = self.env['hr.smart.utils'].compute_duration_difference(lend_id.employee_id, lend_date_from, date_to, True, True, True)
            # case 1: one salary grid for all the periode
            if len(res) == 1:
                res = res[0]
                duration_in_month = res['days']
                grid_id = res['grid_id']
                basic_salary = res['basic_salary']
                if grid_id and duration_in_month > 0:
                    # 1) نسبة الراتب
                    amount = ((duration_in_month * (basic_salary / 30) * lend_id.salary_proportion) / 100.0) * -1
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
                    amount = ((lend_id.lend_salary - lend_id.basic_salary) / 30) * duration_in_month
                    if amount > 0:
                        vals = {'difference_id': self.id,
                                'name': 'فرق الراتب',
                                'employee_id': lend_id.employee_id.id,
                                'number_of_days': duration_in_month,
                                'number_of_hours': 0.0,
                                'amount': amount,
                                'type': 'lend'}
                        line_ids.append(vals)
            # case 2: many salary grid for all the periode
            else:
                mydict = {}
                for rec in res:
                    duration_in_month = rec['days']
                    grid_id = rec['grid_id']
                    basic_salary = rec['basic_salary']
                    if grid_id and duration_in_month > 0:
                        # 1) نسبة الراتب
                        amount = ((duration_in_month * (basic_salary / 30) * lend_id.salary_proportion) / 100.0) * -1
                        mydict['duration_in_month'] += duration_in_month
                        mydict['amount'] += amount
                if mydict:
                    vals = {'difference_id': self.id,
                            'name': 'نسبة الراتب',
                            'employee_id': lend_id.employee_id.id,
                            'number_of_days': mydict['duration_in_month'],
                            'number_of_hours': 0.0,
                            'amount': mydict['amount'],
                            'type': 'lend'}
                    line_ids.append(vals)
                mydict = {}
                for rec in res:
                    duration_in_month = rec['days']
                    grid_id = rec['grid_id']
                    basic_salary = rec['basic_salary']
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
                    amount = ((lend_id.lend_salary - lend_id.basic_salary) / 30) * duration_in_month
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
        holidays_ids = self.env['hr.holidays'].search([('employee_id', '=', self.employee_id.id),
                                                       ('state', '=', 'done')
                                                       ])
        holiday_status_maternity = self.env.ref('smart_hr.data_hr_holiday_status_maternity')
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
            if grid_id and not holiday_status_id.salary_spending and not holiday_status_id.percentages:
                amount = (duration_in_month * (basic_salary / 30))
                if duration_in_month > 0 and amount != 0:
                    vals = {'difference_id': self.id,
                            'name': holiday_id.holiday_status_id.name,
                            'employee_id': holiday_id.employee_id.id,
                            'number_of_days': duration_in_month,
                            'number_of_hours': 0.0,
                            'amount': amount * -1,
                            'type': 'holiday'}
                    line_ids.append(vals)
            # case of  لا يصرف له راتب كامل
            if grid_id and not holiday_status_id.salary_spending and holiday_status_id.percentages:
                for rec in holiday_status_id.percentages:
                    if entitlement_type == rec.entitlement_id.entitlment_category and rec.month_from <= months_from_holiday_start <= rec.month_to:
                        amount = (duration_in_month * (basic_salary / 30) * (100 - rec.salary_proportion)) / 100.0
                        if holiday_status_maternity == holiday_status_id:
                            retirement_amount = basic_salary * grid_id.retirement / 100.0
                            amount = ((basic_salary - retirement_amount) * (100 - rec.salary_proportion)) / 100.0
                            diff = holiday_status_maternity.min_amount - (((basic_salary - retirement_amount)) * (rec.salary_proportion)) / 100.0
                            if diff > 0:
                                amount -= diff
                            print '--amount---', amount
                            # amout depend of number of days
                            amount = amount * duration_in_month / 30
                            print '--basic_salary---', basic_salary
                            print '--retirement_amount---', retirement_amount
                            print '--basic_salary-retirement_amount---', basic_salary - retirement_amount
                            print '--75%---', ((basic_salary - retirement_amount) * (100 - rec.salary_proportion)) / 100.0
                            print '--25%---', ((basic_salary - retirement_amount) * (rec.salary_proportion)) / 100.0
                            print '--1500 - 25%---', holiday_status_maternity.min_amount - (((basic_salary - retirement_amount)) * (rec.salary_proportion)) / 100.0
                            print '--amount---', amount
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
                    amount = (holiday_id.token_compensation_stock * (basic_salary / 30))
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

        date_start_month = str(self.period_id.date_start)
        date_end_month = str(self.period_id.date_stop)

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
                                                           ('employee_id', '=', self.employee_id.id),
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
                                                           ('employee_id', '=', self.employee_id.id),
                                                           ('suspension_end_id', '=', False)
                                                           ])
        suspension_ids += self.env['hr.suspension'].search([('suspension_date', '>=', self.date_from),
                                                            ('suspension_date', '<=', self.date_to),
                                                            ('state', '=', 'done'),
                                                            ('employee_id', '=', self.employee_id.id),
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
                                                           ('employee_id', '=', self.employee_id.id),
                                                           ('suspension_end_id', '=', False)
                                                           ])
        suspension_ids += self.env['hr.suspension'].search([('suspension_date', '<', self.date_from),
                                                            ('state', '=', 'done'),
                                                            ('employee_id', '=', self.employee_id.id),
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
                                                           ('employee_id', '=', self.employee_id.id),
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
                retirement_amount = basic_salary * salary_grid.retirement / 100.0
                amount += (basic_salary - retirement_amount) / 30.0 / 2.0
                date_start = date_start + relativedelta(days=1)
            if _all_days_in_month(suspension['date_from'], suspension['date_to']):
                number_of_days = 30.0
                retirement_amount = basic_salary * salary_grid.retirement / 100.0
                amount += (30 - suspension_number_of_days) * (basic_salary - retirement_amount) / 30.0 / 2.0
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
                           'name': 'فرق %s كف اليد' % allowance.allowance_id.name.encode('utf-8'),
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
                                                             ('employee_id', '=', self.employee_id.id),
                                                             ('state', '=', 'done')
                                                             ])
        for termination in termination_ids:
            grid_id, basic_salary = termination.employee_id.get_salary_grid_id(termination.date)
            if grid_id:
                # فرق الأيام المخصومة من الشهر
                date_from = self.date_from
                date_to = termination.date
                worked_days = days_between(date_from, date_to) - 1
                unworked_days = 30 - worked_days
                if unworked_days > 0:
                    amount = (basic_salary / 30.0) * unworked_days
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
                                'number_of_days': (termination.termination_type_id.nb_salaire - 1) * 30,
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
                    amount = (basic_salary / 30) * termination.termination_type_id.max_days
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
                    amount = (basic_salary / 30) * sum_days
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
        difference_history_ids = self.env['hr.payslip.difference.history'].search([('month', '=', fields.Date.from_string(self.date_from).month),
                                                                                   ('employee_id', '=', self.employee_id.id),
                                                                                   ])
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

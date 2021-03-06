# -*- coding: utf-8 -*-


from openerp import models, fields, api
from datetime import timedelta
from dateutil.relativedelta import relativedelta
from openerp.addons.smart_base.util.time_util import days_between
from openerp.addons.smart_base.util.umalqurra import *


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.multi
    def compute_deductions(self, allowance_total):
        # الحسميات

        line_ids = []
        #  حسم‬  الغياب‬ يكون‬ من‬  جميع البدلات . و  الراتب‬ الأساسي للموظفين‬ الرسميين‬ والمستخدمين
        abscence_ids = self.env['hr.employee.absence.detail'].search([('is_paied', '=', False),
                                                                      ('absence_days_id.employee_id', '=', self.employee_id.id),
                                                                      ('absence_days_id.request_id.state', '=', 'done')
                                                                      ])

        number_of_days = 0
        amount_basic_salary = 0.0
        retirement_amount = 0.0
        for line in abscence_ids:
            salary_grid, basic_salary = self.employee_id.get_salary_grid_id(line.date)
            amount_basic_salary += (basic_salary + allowance_total) / 30.0
            retirement_amount += basic_salary * salary_grid.retirement / 100.0 / 30.0
            number_of_days += 1

        if abscence_ids:
            self.abscence_ids = abscence_ids.ids
            vals = {'name': 'غياب بدون عذر',
                    'employee_id': self.employee_id.id,
                    'number_of_days': number_of_days,
                    'number_of_hours': 0.0,
                    'amount': -1 * amount_basic_salary,
                    'category': 'deduction',
                    'type': 'absence'}
            line_ids.append(vals)
            if retirement_amount != 0:
                vals = {'name': 'فرق التقاعد: غياب بدون عذر',
                        'employee_id': self.employee_id.id,
                        'number_of_days': number_of_days,
                        'number_of_hours': 0.0,
                        'amount': retirement_amount,
                        'category': 'deduction',
                        'type': 'absence'}
                line_ids.append(vals)

        # حسم‬  التأخير يكون‬ من‬  الراتب‬ الأساسي فقط
        delays_ids = self.env['hr.employee.delay.hours'].search([('deduction', '=', False),
                                                                 ('employee_id', '=', self.employee_id.id),
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
                    'type': 'retard_leave',
                    'model_name': 'hr.employee.delay.hours',
                    'object_id': line.id}
            line_ids.append(vals)
        if delays_ids:
            self.delays_ids = delays_ids.ids

        # عقوبة
        sanction_line_ids = self.env['hr.sanction.ligne'].search([('deduction', '=', False),
                                                                  ('sanction_id.type_sanction.deduction', '=', True),
                                                                  ('employee_id', '=', self.employee_id.id),
                                                                  ('sanction_id.state', '=', 'done')
                                                                  ])

        res_sanction_line_ids = []
        for sanction in sanction_line_ids:
            amount = 0.0
            # عدد أيام
            if sanction.days_number and not sanction.days_difference:
                amount = (basic_salary + allowance_total) / 30.0 * sanction.days_number
            # مبلغ
            if sanction.amount and not sanction.amount_difference:
                amount = sanction.amount
            if amount:
                vals = {'name': sanction.type_sanction.name,
                        'employee_id': sanction.employee_id.id,
                        'rate': sanction.days_number,
                        'number_of_days': sanction.days_number,
                        'amount': amount * -1,
                        'category': 'deduction',
                        'type': 'sanction',
                        }
                line_ids.append(vals)
                res_sanction_line_ids.append(sanction.id)
            # الفروقات بالأيام
            if sanction.days_difference > 0:
                multiplication = -1
            if sanction.days_difference < 0:
                multiplication = 1
            if sanction.days_difference:
                amount_difference = (basic_salary + allowance_total) / 30.0 * abs(sanction.days_difference)
                vals = {'name': sanction.type_sanction.name,
                        'employee_id': sanction.employee_id.id,
                        'rate': sanction.days_number,
                        'number_of_days': abs(sanction.days_difference),
                        'amount': amount_difference * multiplication,
                        'category': 'deduction',
                        'type': 'sanction',
                        }
                line_ids.append(vals)
                res_sanction_line_ids.append(sanction.id)
            # الفروقات بالمبلغ
            if sanction.amount_difference > 0:
                multiplication = -1
            if sanction.amount_difference < 0:
                multiplication = 1
            if sanction.amount_difference:
                amount_difference = sanction.amount_difference
                vals = {'name': sanction.type_sanction.name,
                        'employee_id': sanction.employee_id.id,
                        'rate': sanction.days_number,
                        'number_of_days': sanction.days_number,
                        'amount': amount_difference * multiplication,
                        'category': 'deduction',
                        'type': 'sanction',
                        }
                line_ids.append(vals)
                res_sanction_line_ids.append(sanction.id)
        self.sanction_line_ids = res_sanction_line_ids
        # فرق الحسميات المتخلدة
        line_ids += self.get_difference_one_third_salary(self.date_from, self.date_to, self.employee_id)

        return line_ids

    @api.multi
    def get_difference_one_third_salary(self, date_from, date_to, employee_id):
        self.ensure_one()
        line_ids = []
        domain = [('payslip_id.employee_id', '=', employee_id.id),
                  ('period_id', '=', self.period_id.id),
                  ]
        difference_history_ids = self.env['hr.payslip.difference.history'].search(domain)
        for difference_history in difference_history_ids:
            name = ''
            if difference_history.name == 'third_salary':
                name = 'فرق حسميات أكثر من ثلث الراتب مرحلة من الشهر الفارط'
            elif difference_history.name == 'negative_salary':
                name = 'المبلغ المؤجل (سبب راتب سالب)'
            vals = {'name': name,
                    'employee_id': difference_history.payslip_id.employee_id.id,
                    'number_of_days': 0.0,
                    'number_of_hours': 0.0,
                    'amount': difference_history.amount * -1.0,
                    'category': 'deduction',
                    'type': 'one_third_salary'}
            line_ids.append(vals)
        return line_ids

    @api.multi
    def compute_differences(self):
        # احتساب الأثر المالي
        line_ids = []
        decision_appoint = False
        compute_date_from = False
        compute_date_to = False
        # case 1: احتساب الأثر المالي لهذا الشهر
        # case 2: احتساب الأثر المالي  لشهر الفارط من تاريخ إعداد مسير الشهر الفرط إلى تاريخ بداية هذا الشهر
        # get last payslip for current employee
        last_payslip = self.env['hr.payslip'].search([('employee_id', '=', self.employee_id.id),
                                                      ('is_special', '=', False),
                                                      ('date_from', '<', self.date_from),
                                                      ('state', '=', 'done')], limit=1, order='date_from desc')
        if last_payslip:
            # add one day to compute_date of last payslip
            compute_date_from = str(fields.Date.from_string(last_payslip.compute_date) + timedelta(days=1))
            compute_date_to = last_payslip.date_to
        # إذا لم يكن للموظف مسير في الشهر الفارط ، ربما يكون قد عين ( تعيين جديد)
        #  بعد إعداد الرواتب للشهر الفارط لذلك يجب احتساب فرق أيام الشهر الفارط
        # بداية من تاريخ تفعيل التعيين
        else:
            type_appointment_id = self.env.ref('smart_hr.data_hr_new_agent_public').id
            decision_appoint = self.env['hr.decision.appoint'].search([('is_started', '=', True),
                                                                       ('type_appointment', '=', type_appointment_id),
                                                                       ('state_appoint', '=', 'active'),
                                                                       ('date_direct_action', '!=', False),
                                                                       ('employee_id', '=', self.employee_id.id),
                                                                       ], order="date_direct_action desc", limit=1)
            if decision_appoint:
                compute_date_from = decision_appoint.date_direct_action
                compute_date_to = str(fields.Date.from_string(self.date_from) - timedelta(days=1))

        # فروقات  تعيين موظف جديد  :
        #  ربما يكون الموظف قد عين ( تعيين جديد) بعد إعداد الرواتب للشهر الفارط لذلك يجب
        #   اعطائه مسير الشهر الفارط خلال هذا الشهر ( أساسي ، بدلات، تقاعد) بداية من تاريخ مباشرته  العمل
        if decision_appoint:
            line_ids += self.get_difference_new_employee(compute_date_from, compute_date_to)
        # فروقات النقل : يتم احتساب الأثار المالي للنقل في نفس حالة التعين
        # فروقات التعين
        line_ids += self.get_difference_decision_appoint(self.date_from, self.date_to, self.employee_id, False)
        if compute_date_from and compute_date_to:
            line_ids += self.get_difference_decision_appoint(compute_date_from, compute_date_to, self.employee_id, True)
        # فروقات التكليف
        line_ids += self.get_difference_assign(self.date_from, self.date_to, self.employee_id, False)
        if compute_date_from and compute_date_to:
            line_ids += self.get_difference_assign(compute_date_from, compute_date_to, self.employee_id, True)
        # فروقات الإبتعاث
        line_ids += self.get_difference_scholarship(self.date_from, self.date_to, self.employee_id, False)
        if compute_date_from and compute_date_to:
            line_ids += self.get_difference_scholarship(compute_date_from, compute_date_to, self.employee_id, True)
        # فروقات الإعارة
        line_ids += self.get_difference_lend(self.date_from, self.date_to, self.employee_id, False)
        if compute_date_from and compute_date_to:
            line_ids += self.get_difference_lend(compute_date_from, compute_date_to, self.employee_id, True)
        # فروقات الإجازة
        line_ids += self.get_difference_holidays(self.date_from, self.date_to, self.employee_id, False)
        if compute_date_from and compute_date_to:
            line_ids += self.get_difference_holidays(compute_date_from, compute_date_to, self.employee_id, True)
        # فروقات كف اليد
        line_ids += self.get_difference_suspension(self.date_from, self.date_to, self.employee_id, last_payslip, False)
        if compute_date_from and compute_date_to:
            # تحتسب من يوم تاريخ ترحيل الراتب السابق وليس تاريخ الراتب  زائد يوم
            compute_date_from_suspension = compute_date_from
            if last_payslip:
                compute_date_from_suspension = last_payslip.compute_date
            line_ids += self.get_difference_suspension(compute_date_from_suspension, compute_date_to, self.employee_id, last_payslip, True)
        # فروقات طى القيد
        line_ids += self.get_difference_termination(self.date_from, self.date_to, self.employee_id, False)
        if compute_date_from and compute_date_to:
            line_ids += self.get_difference_termination(compute_date_from, compute_date_to, self.employee_id, True)
        return line_ids

    @api.multi
    def get_difference_new_employee(self, date_from, date_to):
        self.ensure_one()
        line_ids = []
        employee = self.employee_id
        salary_grid, basic_salary = employee.get_salary_grid_id(date_from)
        if not salary_grid:
            return
        number_of_days = days_between(date_from, date_to)
        # --------------
        # 1- الراتب الأساسي
        # --------------
        amount = basic_salary / 30.0 * number_of_days
        basic_salary_val = {'name': u'فرق الراتب الأساسي للشهر الفارط',
                            'employee_id': employee.id,
                            'rate': 0.0,
                            'number_of_days': number_of_days,
                            'number_of_hours': 0.0,
                            'amount': amount,
                            'category': 'basic_salary',
                            'type': 'basic_salary',
                            }
        line_ids.append(basic_salary_val)
        # --------------
        # 2- البدلات القارة
        # --------------
        for allowance in employee.get_employee_allowances(salary_grid):
            amount = allowance['amount'] / 30.0 * number_of_days
            allowance_val = {'name': u'فرق ' + allowance['allowance_name'] + u' للشهر الفارط ',
                             'employee_id': employee.id,
                             'rate': 0.0,
                             'number_of_days': number_of_days,
                             'number_of_hours': 0.0,
                             'amount': amount,
                             'category': 'allowance',
                             'type': 'allowance',
                             }
            line_ids.append(allowance_val)
        # --------------
        # 3- التقاعد
        # --------------
        retirement_amount = -1.0 * basic_salary * salary_grid.retirement / 100.0 / 30.0 * number_of_days
        if retirement_amount:
            retirement_val = {'name': u'فرق التقاعد للشهر الفارط',
                              'employee_id': employee.id,
                              'rate': 0.0,
                              'number_of_days': number_of_days,
                              'number_of_hours': 0.0,
                              'amount': retirement_amount,
                              'category': 'deduction',
                              'type': 'retirement'
                              }
            line_ids.append(retirement_val)
        # --------------
        # 4- التأمينات
        # --------------
        insurance_amount = -1.0 * basic_salary * salary_grid.insurance / 100.0 / 30.0 * number_of_days
        if insurance_amount:
            insurance_val = {'name': u'فرق التأمين للشهر الفارط',
                             'employee_id': employee.id,
                             'rate': 0.0,
                             'number_of_days': number_of_days,
                             'number_of_hours': 0.0,
                             'amount': insurance_amount,
                             'category': 'deduction',
                             'type': 'insurance'
                             }
            line_ids.append(insurance_val)
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
            # minus one day to date_from
            new_date_from = str(fields.Date.from_string(date_from) - timedelta(days=1))
            domain.append(('done_date', '>=', new_date_from))
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
            # minus one day to date_from
            new_date_from = str(fields.Date.from_string(date_from) - timedelta(days=1))
            domain.append(('done_date', '>=', new_date_from))
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
            date_start, date_stop = self.env['hr.smart.utils'].get_overlapped_periode(date_from, date_to, assign_date_from, assign_date_to)
            if date_start and date_stop:
                res = self.env['hr.smart.utils'].compute_duration_difference(assign_id.employee_id, date_start, date_stop, True, True, True)
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
                vals = {'name': u'تكليف : فرق الراتب الذي توفره الجهة' + name,
                        'employee_id': assign_id.employee_id.id,
                        'number_of_days': duration_in_month,
                        'number_of_hours': 0.0,
                        'amount': salary_rate_amount,
                        'type': 'commissioning'}
                line_ids.append(vals)
            if amount_allowance < 0:
                vals = {'name': u'تكليف : فرق بدل النقل الذي توفره الجهة' + name,
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
            # minus one day to date_from
            new_date_from = str(fields.Date.from_string(date_from) - timedelta(days=1))
            domain.append(('done_date', '>=', new_date_from))
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
            date_start, date_stop = self.env['hr.smart.utils'].get_overlapped_periode(date_from, date_to, scholarship_date_from, scholarship_date_to)
            if date_start and date_stop:
                res = self.env['hr.smart.utils'].compute_duration_difference(scholarship_id.employee_id, date_start, date_stop, True, True, True)
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
                vals = {'name': u': ابتعاث ' + allowance.name + name  ,
                        'employee_id': scholarship_id.employee_id.id,
                        'number_of_days': duration_in_month,
                        'number_of_hours': 0.0,
                        'amount': allow_exception_amount,
                        'type': 'scholarship'}
                line_ids.append(vals)
            # 2) نسبة الراتب بعد حسم التقاعد
            if final_retirement_amount < 0:
                vals = {'name': u'ابتعاث :  نسبة الراتب بعد حسم التقاعد' + name,
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
            # minus one day to date_from
            new_date_from = str(fields.Date.from_string(date_from) - timedelta(days=1))
            domain.append(('done_date', '>=', new_date_from))
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
            date_start, date_stop = self.env['hr.smart.utils'].get_overlapped_periode(date_from, date_to, lend_date_from, lend_date_to)
            if date_start and date_stop:
                res = self.env['hr.smart.utils'].compute_duration_difference(lend_id.employee_id, date_start, date_stop, True, True, True)
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
                vals = {'name': u'إعارة : فرق الراتب الذي توفره الجهة ' + name,
                        'employee_id': lend_id.employee_id.id,
                        'number_of_days': duration_in_month,
                        'number_of_hours': 0.0,
                        'amount': amount,
                        'type': 'lend'
                        }
                line_ids.append(vals)

            # 2 -البدلات
            if allowance_amount < 0:
                vals = {'name': u'إعارة : فرق البدلات التي تتحملها الجهة ' + name,
                        'employee_id': lend_id.employee_id.id,
                        'number_of_days': duration_in_month,
                        'number_of_hours': 0.0,
                        'amount': allowance_amount,
                        'type': 'lend'
                        }
                line_ids.append(vals)
            # 3) حصة الحكومة من التقاعد
            if amount_retirement:
                vals = {'name': u'إعارة : حصة الحكومة من التقاعد ' + name,
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
                  ('state', 'in', ('done', 'cutoff'))]
        if for_last_month:
            # minus one day to date_from
            new_date_from = str(fields.Date.from_string(date_from) - timedelta(days=1))
            domain.append(('done_date', '>=', new_date_from))
            domain.append(('done_date', '<=', date_to))
            name = u' للشهر الفارط '
        holidays_ids = self.env['hr.holidays'].search(domain)
        for holiday_id in holidays_ids:
            holiday_status_id = holiday_id.holiday_status_id
            if holiday_status_id.min_amount:
                # add constrainte to payslip: to check after net salary is calculated
                self.env['hr.payroll.constrainte'].create({'payslip_id': self.id,
                                                           'constrainte_name': 'min_amount',
                                                           'amount': holiday_status_id.min_amount})
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
            date_start, date_stop = self.env['hr.smart.utils'].get_overlapped_periode(date_from, date_to, holiday_date_from, holiday_date_to)
            if date_start and date_stop:
                res = self.env['hr.smart.utils'].compute_duration_difference(holiday_id.employee_id, date_start, date_stop, True, True, True)
            basic_salary_amount = 0.0
            basic_salary_amount2 = 0.0
            retirement_amount = 0.0
            retirement_amount2 = 0.0
            allowance_amount = 0.0
            allowance_amount2 = 0.0
            cumulation_days = 0.0
            if len(res) == 1:
                res = res[0]
                grid_id = res['grid_id']
                basic_salary = res['basic_salary']
                duration_in_month = res['days']
                # NOT SALRY SPENDING
                if not holiday_status_id.salary_spending:
                    # فرق الراتب الأساسي
                    basic_salary_amount = (duration_in_month * (basic_salary / 30.0))
                    # فرق البدلات
                    allowance_amount = 0.0
                    if duration_in_month > 0:
                        for allowance in holiday_id.employee_id.get_employee_allowances(grid_id):
                            allowance_amount += allowance['amount'] / 30.0 * duration_in_month
                            if holiday_status_id.transport_allowance and allowance['allowance_id'] == self.env.ref('smart_hr.hr_allowance_type_01').id:
                                allowance_amount -= allowance['amount'] / 30.0 * duration_in_month
                # فرق التقاعد
                if holiday_status_id.deductible_duration_service:
                    retirement_amount = basic_salary * grid_id.retirement / 100.0 / 30.0 * duration_in_month
                # case of  لا يصرف له راتب كامل
                if grid_id and holiday_status_id.salary_spending and holiday_status_id.percentages:
                    for rec in holiday_status_id.percentages:
                        if entitlement_type == rec.entitlement_id.entitlment_category:
                            today = fields.Date.from_string(fields.Date.today())
                            if rec.entitlement_id.periode:
                                get_from_date = today - relativedelta(years=rec.entitlement_id.periode)
                                get_to_date = today
                                # get first token holiday with same type
                                newest_holiday_id = self.env['hr.holidays'].search([('holiday_status_id', '=', holiday_status_id.id),
                                                                                    ('employee_id', '=', holiday_id.employee_id.id),
                                                                                    ('state', 'in', ('done', 'cutoff')),
                                                                                    ], order='date_from', limit=1)
                                if newest_holiday_id:
                                    get_to_date = fields.Date.from_string(newest_holiday_id.date_to)
                                    get_from_date = get_to_date - relativedelta(years=rec.entitlement_id.periode)
                                # get token holidays started in  get_from_date and before start of month
                                start_month = fields.Date.from_string(self.date_from)
                                ranges = []
                                before_holidays = self.env['hr.holidays'].search([('holiday_status_id', '=', holiday_status_id.id),
                                                                                  ('employee_id', '=', holiday_id.employee_id.id),
                                                                                  ('state', 'in', ('done', 'cutoff')),
                                                                                  ('date_from', '>=', get_from_date),
                                                                                  ('date_from', '<', start_month),
                                                                                  ])
                                for b_hol in before_holidays:
                                    range_p = [fields.Date.from_string(b_hol.date_from), start_month]
                                    ranges.append(range_p)
                                cumulation_days = self.env['hr.smart.utils'].get_overlapped_days(get_from_date, get_to_date, ranges)
                                cumulation_days += duration_in_month
                                months_from_holiday_start = cumulation_days / 30.0
                            if rec.month_from <= months_from_holiday_start < rec.month_to and duration_in_month > 0:
                                ret_amount = basic_salary * grid_id.retirement / 100.0
                                new_basic_salary = basic_salary - ret_amount + retirement_amount
                                basic_salary_amount = (duration_in_month * (new_basic_salary / 30.0) * (100 - rec.salary_proportion)) / 100.0
                                if holiday_status_id.min_amount:
                                    basic_salary_amount = (new_basic_salary * (100 - rec.salary_proportion)) / 100.0
                                    # amout depend of number of days
                                    basic_salary_amount = basic_salary_amount * duration_in_month / 30.0
                                # فرق البدلات
                                allowance_amount2 = 0.0
                                for allowance in holiday_id.employee_id.get_employee_allowances(grid_id):
                                    if not holiday_status_id.transport_allowance and allowance['allowance_id'] == self.env.ref('smart_hr.hr_allowance_type_01').id:
                                        allowance_amount2 += allowance['amount'] / 30.0 * duration_in_month
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
                            for allowance in holiday_id.employee_id.get_employee_allowances(grid_id):
                                allowance_amount += allowance['amount'] / 30.0 * days
                                if holiday_status_id.transport_allowance and allowance['allowance_id'] == self.env.ref('smart_hr.hr_allowance_type_01').id:
                                    allowance_amount -= allowance['amount'] / 30.0 * days
                    # فرق التقاعد
                    if holiday_status_id.deductible_duration_service:
                        retirement_amount += basic_salary * grid_id.retirement / 100.0 / 30.0 * days
                    # case of  لا يصرف له راتب كامل
                    if grid_id and holiday_status_id.salary_spending and holiday_status_id.percentages:
                        for per in holiday_status_id.percentages:
                            if entitlement_type == per.entitlement_id.entitlment_category:
                                today = fields.Date.from_string(fields.Date.today())
                                if per.entitlement_id.periode:
                                    # the above code must be entred one only for one time
                                    if not months_from_holiday_start:
                                        get_from_date = today - relativedelta(years=per.entitlement_id.periode)
                                        get_to_date = today
                                        # get first token holiday with same type
                                        newest_holiday_id = self.env['hr.holidays'].search([('holiday_status_id', '=', holiday_status_id.id),
                                                                                            ('employee_id', '=', holiday_id.employee_id.id),
                                                                                            ('state', 'in', ('done', 'cutoff')),
                                                                                            ], order='date_from', limit=1)
                                        if newest_holiday_id:
                                            get_to_date = fields.Date.from_string(newest_holiday_id.date_to)
                                            get_from_date = get_to_date - relativedelta(years=per.entitlement_id.periode)
                                        # get token holidays started in  get_from_date and before start of month
                                        start_month = fields.Date.from_string(self.date_from)
                                        ranges = []
                                        before_holidays = self.env['hr.holidays'].search([('holiday_status_id', '=', holiday_status_id.id),
                                                                                          ('employee_id', '=', holiday_id.employee_id.id),
                                                                                          ('state', 'in', ('done', 'cutoff')),
                                                                                          ('date_from', '>=', get_from_date),
                                                                                          ('date_from', '<', start_month),
                                                                                          ])
                                        for b_hol in before_holidays:
                                            if fields.Date.from_string(b_hol.date_to) < start_month:
                                                range_p = [b_hol.date_from, b_hol.date_to]
                                                ranges.append(range_p)
                                        cumulation_days = self.env['hr.smart.utils'].get_overlapped_days(get_from_date, get_to_date, ranges)
                                        cumulation_days += duration_in_month
                                        months_from_holiday_start = cumulation_days / 30.0
                                if entitlement_type == per.entitlement_id.entitlment_category and per.month_from <= months_from_holiday_start <= per.month_to and days > 0:
                                    ret_amount = basic_salary * grid_id.retirement / 100.0
                                    new_basic_salary = basic_salary - ret_amount + retirement_amount
                                    basic_salary_amount2 += (days * (new_basic_salary / 30.0) * (100 - per.salary_proportion)) / 100.0
                                    if holiday_status_id.min_amount:
                                        basic_salary_amount2 += (new_basic_salary * (100 - per.salary_proportion)) / 100.0
                                        diff = holiday_status_id.min_amount - (new_basic_salary * per.salary_proportion) / 100.0
                                        if diff > 0:
                                            basic_salary_amount2 -= diff
                                        # amout depend of number of days
                                        basic_salary_amount2 += basic_salary_amount2 * days / 30.0
                                # فرق البدلات
                                allowance_amount2 = 0.0
                                for allowance in holiday_id.employee_id.get_employee_allowances(grid_id):
                                    if not holiday_status_id.transport_allowance and allowance['allowance_id'] == self.env.ref('smart_hr.hr_allowance_type_01').id:
                                        allowance_amount2 += allowance['amount'] / 30.0 * days
                                # فرق التقاعد
                                if holiday_status_id.deductible_duration_service:
                                    retirement_amount2 += (basic_salary * grid_id.retirement / 100.0 * (100 - per.salary_proportion) / 100.0) / 30.0 * days
            #
            if basic_salary_amount:
                vals = {'name': holiday_id.holiday_status_id.name + name,
                        'employee_id': holiday_id.employee_id.id,
                        'number_of_days': duration_in_month,
                        'number_of_hours': 0.0,
                        'amount': basic_salary_amount * -1,
                        'type': 'holiday'}
                line_ids.append(vals)

            if allowance_amount:
                vals = {'name': u'فرق بدلات ' + holiday_id.holiday_status_id.name + name,
                        'employee_id': holiday_id.employee_id.id,
                        'number_of_days': duration_in_month,
                        'number_of_hours': 0.0,
                        'amount': allowance_amount * -1,
                        'type': 'holiday'}
                line_ids.append(vals)
            # فرق التقاعد
            if retirement_amount != 0:
                vals = {'name': u'فرق التقاعد‬ ' + holiday_id.holiday_status_id.name + name,
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
                vals = {'name': u' حسم بدل النقل  ' + holiday_id.holiday_status_id.name + name,
                        'employee_id': holiday_id.employee_id.id,
                        'number_of_days': duration_in_month,
                        'number_of_hours': 0.0,
                        'amount': allowance_amount2 * -1,
                        'type': 'holiday'}
                line_ids.append(vals)
            # فرق التقاعد
            if retirement_amount2:
                vals = {'name': u'فرق التقاعد‬ : ' + holiday_id.holiday_status_id.name + name,
                        'employee_id': holiday_id.employee_id.id,
                        'number_of_days': duration_in_month,
                        'number_of_hours': 0.0,
                        'amount': retirement_amount2,
                        'type': 'holiday'}
                line_ids.append(vals)
            # case of  نوع التعويض    مقابل ‫مادي‬ ‬   اجازة التعويض
            grid_id, basic_salary = employee_id.get_salary_grid_id(self.date_from)
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
    def get_difference_suspension(self, date_from, date_to, employee_id, last_payslip, for_last_month):
        # # إذا كان كف اليد على كامل الشهر الحالي فيجب احتساب الفرق على أساس  30 يوم   وإلا فيحتسب على عدد أيام الكف.
        # إذا كان عدد أيام الشهر أصغر من 30 يتم احتساب قيمة أيام فرق  مساوي إلى قيمة أخر يوم في الشهر.
        # مثلا شهر فيه 28 يوم يكون  قيمة يوم 29 و-30 مساوي لقيمة يوم 28.

        self.ensure_one()
        suspension_obj = self.env['hr.suspension']
        # get all operations(hr.suspension) in latest month
        domain_last_month = []
        name = ''
        if for_last_month:
            # for_last_month remove  operations added in the old payslip
            operations_ids = last_payslip.get_operations('hr.suspension')
            operations_end_ids = last_payslip.get_operations('hr.suspension.end')
            domain_last_month = [('id', 'not in', operations_ids)]
            name = u' للشهر الفارط '
        date_from_param = date_from
        date_to_param = date_to
        line_ids = []
        all_suspensions = []
        # -------------
        # get  started and ended suspension in current month
        # -------------
        # إذا كان تاريخ الكف وتاريخ إنهاء الكف في نفس الشهر  فلا يتم حسم وإرجاع فقط يتم حسم إذا كان معاقب
        domain = [('suspension_date', '>=', date_from),
                  ('suspension_date', '<=', date_to),
                  ('state', '=', 'done'),
                  ('suspension_end_id.release_date', '>=', date_from),
                  ('suspension_end_id.release_date', '<=', date_to),
                  ('employee_id', '=', employee_id.id),
                  ('suspension_end_id.state', '=', 'done'),
                  ]
        domain += domain_last_month
        suspension_ids = suspension_obj.search(domain)
        for suspension in suspension_ids:
            date_from_s = suspension.suspension_date
            date_to_s = suspension.suspension_end_id.release_date
            # if date_from < date_from:
            #     date_from = date_from
            # if date_to > date_to:
            #     date_to = date_to
            number_of_days = days_between(date_from_s, date_to_s)
            if number_of_days > 1:
                all_suspensions.append({'employee_id': suspension.employee_id.id,
                                        'res_id': suspension.id, 'sup_end_res_id': suspension.suspension_end_id.id,
                                        'date_from': date_from_s, 'date_to': date_to_s,
                                        'number_of_days': number_of_days, 'return': False})
                if not suspension.suspension_end_id.condemned:
                    all_suspensions.append({'employee_id': suspension.employee_id.id,
                                            'res_id': suspension.id, 'sup_end_res_id': suspension.suspension_end_id.id,
                                            'date_from': date_from_s, 'date_to': date_to_s,
                                            'number_of_days': number_of_days, 'return': True})
        # -------------
        # get started suspension in this month and not ended in current month or dont have yet an end
        # --------------
        domain = [('suspension_date', '>=', date_from),
                  ('suspension_date', '<=', date_to),
                  ('state', '=', 'done'),
                  ('employee_id', '=', employee_id.id),
                  ('suspension_end_id', '=', False)
                  ]
        domain += domain_last_month
        suspension_ids = suspension_obj.search(domain)
        domain = [('suspension_date', '>=', date_from),
                  ('suspension_date', '<=', date_to),
                  ('state', '=', 'done'),
                  ('employee_id', '=', employee_id.id),
                  ('suspension_end_id.release_date', '>', date_to),
                  ('suspension_end_id.state', '=', 'done'),
                  ]
        domain += domain_last_month
        suspension_ids += suspension_obj.search(domain)
        for suspension in suspension_ids:
            date_from_s = suspension.suspension_date
            date_to_s = date_to
            number_of_days = days_between(date_from_s, date_to_s)
            if number_of_days > 1:
                all_suspensions.append({'employee_id': suspension.employee_id.id, 'res_id': suspension.id,
                                        'date_from': date_from_s, 'date_to': date_to_s,
                                        'number_of_days': number_of_days, 'return': False})
        # -------------
        # get started suspension before this month and not yet ended
        # -------------

        domain = [('suspension_date', '<', date_from),
                  ('state', '=', 'done'),
                  ('employee_id', '=', employee_id.id),
                  ('suspension_end_id', '=', False)
                  ]
        domain += domain_last_month
        suspension_ids = suspension_obj.search(domain)
        domain = [('suspension_date', '<', date_from),
                  ('state', '=', 'done'),
                  ('employee_id', '=', employee_id.id),
                  ('suspension_end_id.release_date', '>', date_to),
                  ('suspension_end_id.state', '=', 'done'),
                  ]
        domain += domain_last_month
        suspension_ids += suspension_obj.search(domain)
        for suspension in suspension_ids:
            date_from_s = date_from
            date_to_s = date_to
            number_of_days = days_between(date_from_s, date_to_s)
            if number_of_days > 1:
                all_suspensions.append({'employee_id': suspension.employee_id.id, 'res_id': suspension.id,
                                        'date_from': date_from_s, 'date_to': date_to_s,
                                        'number_of_days': number_of_days, 'return': False})
        # -----------------
        # get started suspension before this month and ended in current month
        # -----------------

        domain = [('suspension_date', '<', date_from),
                  ('state', '=', 'done'),
                  ('employee_id', '=', employee_id.id),
                  ('suspension_end_id.release_date', '>=', date_from),
                  ('suspension_end_id.release_date', '<=', date_to),
                  ('suspension_end_id.state', '=', 'done'),
                  ]
        domain += domain_last_month
        suspension_ids = suspension_obj.search(domain)
        for suspension in suspension_ids:
            date_from_s = date_from
            date_to_s = suspension.suspension_end_id.release_date
            number_of_days = days_between(date_from_s, date_to_s)
            if number_of_days > 1:
                all_suspensions.append({'employee_id': suspension.employee_id.id,
                                        'res_id': suspension.id, 'sup_end_res_id': suspension.suspension_end_id.id,
                                        'date_from': date_from_s, 'date_to': date_to_s,
                                        'number_of_days': number_of_days, 'return': False})
            # case 1: not condemned:
            if not suspension.suspension_end_id.condemned:
                date_from_s = suspension.suspension_date
                date_to_s = suspension.suspension_end_id.release_date
                number_of_days = days_between(date_from_s, date_to_s)
                if number_of_days > 1:
                    all_suspensions.append({'employee_id': suspension.employee_id.id,
                                            'res_id': suspension.id, 'res_id': suspension.id, 'sup_end_res_id': suspension.suspension_end_id.id,
                                            'date_from': date_from_s, 'date_to': date_to_s,
                                            'number_of_days': number_of_days, 'return': True})

        # -------------
        # get suspensions added in latest month (started in month or before)
        # and ended in this month , and the suspension end is created after compute payslip
        # c-a-d  : this suspension exist in operation_ids but the suspension end dont exist
        # this cas only for for_last_month.
        # -------------
        if for_last_month:
            domain = [('id', 'in', operations_ids),
                      # ('suspension_end_id.release_date', '>=', date_from),
                      # ('suspension_end_id.release_date', '<=', date_to),
                      # ('suspension_end_id.state', '=', 'done'),
                      # ('suspension_end_id.state', '=', 'done'),
                      ('suspension_end_id.id', 'not in', operations_end_ids),

                      ]
            suspension_ids = suspension_obj.search(domain)
            for suspension in suspension_ids:
                # 1 - إرجاع من تاريخ نهاية الكف  إلى نهاية الشهر (لأنه تم  حسمها الشهر الفارط و هي خارجة عن مدة الكف) فترجع
                # لا يحتسب تاريخ إطلاق السراح ، يحتسب في عملية إرجاع مدة الكف
                date_from_s = suspension.suspension_end_id.release_date
                date_from_s = str(fields.Date.from_string(date_from_s) + timedelta(days=1))
                date_to_s = date_to
                number_of_days = days_between(date_from_s, date_to)
                if number_of_days > 1:
                    all_suspensions.append({'employee_id': suspension.employee_id.id,  # 'res_id': suspension.id, dont add it again
                                            'date_from': date_from_s, 'date_to': date_to_s,
                                            'number_of_days': number_of_days, 'return': True})
                # 2 - إرجاع فترة الكف
                if not suspension.suspension_end_id.condemned:
                    date_from_s = suspension.suspension_date
                    date_to_s = suspension.suspension_end_id.release_date
                    number_of_days = days_between(date_from_s, date_to_s)
                    if number_of_days > 1:
                        all_suspensions.append(
                            {'employee_id': suspension.employee_id.id,  # 'res_id': suspension.id, dont add it again
                             'date_from': date_from_s, 'date_to': date_to_s,
                             'number_of_days': number_of_days, 'return': True})

        # -------------
        # احتساب الفروقات
        # -------------
        new_operation_ids = []
        new_operation_end_ids = []
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
            # إذا  يستوجب حسم فيتم حسم أيام الفترة المطلوبة فقط
            if not suspension['return']:
                date_start, date_stop = self.env['hr.smart.utils'].get_overlapped_periode(date_from, date_to, suspension_date_from, suspension_date_to)
                if date_start and date_stop:
                    res = self.env['hr.smart.utils'].compute_duration_difference(employee_id, date_start, date_stop, True, True, True)
            # إذا فيه إرجاع لازم يتم إرجاع كامل الفترة
            else:
                res = self.env['hr.smart.utils'].compute_duration_difference(employee_id, suspension_date_from, suspension_date_to, True, True, True, False)
            amount = 0.0
            allowance_amount = 0.0
            multiplication = -1.0
            operation_name = u'حسم '
            if suspension['return']:
                multiplication = 1.0
                operation_name = u'إرجاع '
            for rec in res:
                grid_id = rec['grid_id']
                basic_salary = rec['basic_salary']
                days = rec['days']
                duration_in_month += days
                retirement_amount = basic_salary * grid_id.retirement / 100.0 / 30.0 * days
                amount += ((basic_salary / 30.0) * days - retirement_amount) / 2.0
                for allowance in employee.get_employee_allowances(grid_id):
                    allowance_amount += allowance['amount'] / 30.0 * days
            # فرق الراتب الأساسي كف اليد
            if amount:
                val = {'name': u'%s فرق الراتب الأساسي كف اليد %s' % (operation_name,name),
                       'employee_id': employee.id,
                       'number_of_days': duration_in_month,
                       'number_of_hours': 0.0,
                       'amount': amount * multiplication,
                       'type': 'suspension',
                       'deducted_from_working_days': not for_last_month and not suspension['return'],
                       }
                line_ids.append(val)
            # 2- البدلات لا تحتسب في حال كان الموظف مكفوف اليد
            if allowance_amount:
                val = {'name': operation_name+u' فرق البدلات كف اليد' + name,
                       'employee_id': employee.id,
                       'number_of_days': duration_in_month,
                       'number_of_hours': 0.0,
                       'amount': allowance_amount * multiplication,
                       'type': 'suspension'}
                line_ids.append(val)
            if (amount or allowance_amount) and suspension.get('res_id', False) and suspension['res_id'] not in new_operation_ids:
                self.operation_ids.create({'res_model': 'hr.suspension', 'res_id': suspension['res_id'], 'payslip_id': self.id})
                new_operation_ids.append(suspension['res_id'])
            if (amount or allowance_amount) and suspension.get('sup_end_res_id', False) and suspension['sup_end_res_id'] not in new_operation_end_ids:
                self.operation_ids.create({'res_model': 'hr.suspension.end', 'res_id': suspension['sup_end_res_id'], 'payslip_id': self.id})
                new_operation_end_ids.append(suspension['sup_end_res_id'])

        return line_ids

    @api.multi
    def get_difference_termination(self, date_from, date_to, employee_id, for_last_month):
        self.ensure_one()
        line_ids = []
        domain = [('employee_id', '=', employee_id.id), ('state', '=', 'done')]
        name = ''
        if for_last_month:
            domain.append(('done_date', '>=', date_from))
            domain.append(('done_date', '<=', date_to))
            name = u' للشهر الفارط '
        termination_ids = self.env['hr.termination'].search(domain)
        for termination in termination_ids:
            # prepare the employee to be ready to close his financial folder
            termination.employee_id.to_be_clear_financial_dues = True
            if termination.date_termination > date_from:
                date_from = termination.date_termination
            res = self.env['hr.smart.utils'].compute_duration_difference(employee_id, date_from, date_to, True, True, True)
            allowance_amount = 0.0
            retirement_amount = 0.0
            basic_salary_amount = 0.0
            duration_in_month = 0.0
            for rec in res:
                grid_id = rec['grid_id']
                basic_salary = rec['basic_salary']
                days = rec['days']
                duration_in_month += days
                retirement_amount += basic_salary * grid_id.retirement / 100.0 / 30.0 * days
                basic_salary_amount += basic_salary / 30.0 * days
                for allowance in termination.employee_id.get_employee_allowances(grid_id):
                    allowance_amount += allowance['amount'] / 30.0 * days
            # الفروقات
            if basic_salary_amount:
                val = {'name': termination.termination_type_id.name + " " + u'(فرق الأيام المخصومة من الشهر)' + name,
                       'employee_id': termination.employee_id.id,
                       'number_of_days': duration_in_month,
                       'number_of_hours': 0.0,
                       'amount': basic_salary_amount * -1.0,
                       'type': 'termination',
                       'deducted_from_working_days': not for_last_month,
                       }
                line_ids.append(val)
            if retirement_amount:
                val = {'name': termination.termination_type_id.name + " " + u'(فرق التقاعد )' + name,
                       'employee_id': termination.employee_id.id,
                       'number_of_days': duration_in_month,
                       'number_of_hours': 0.0,
                       'amount': retirement_amount,
                       'type': 'termination'}
                line_ids.append(val)
            if allowance_amount:
                val = {'name': termination.termination_type_id.name + " " + u'(فرق البدلات )' + name,
                       'employee_id': termination.employee_id.id,
                       'number_of_days': duration_in_month,
                       'number_of_hours': 0.0,
                       'amount': allowance_amount * -1.0,
                       'type': 'termination'}
                line_ids.append(val)
            # المزايا تخص الشهر الحالي فقط
            if not for_last_month:
                grid_id, basic_salary = termination.employee_id.get_salary_grid_id(termination.date)
                # سعودي
                if termination.employee_id.country_id and termination.employee_id.country_id.code_nat == 'SA':
                    if grid_id:
                        # 1) عدد الرواتب المستحق
                        if termination.termination_type_id.nb_salaire > 0:
                            amount = basic_salary * termination.termination_type_id.nb_salaire
                            vals = {'name': termination.termination_type_id.name + " " + u'(عدد الرواتب المستحق	)' + name,
                                    'employee_id': termination.employee_id.id,
                                    'number_of_days': termination.termination_type_id.nb_salaire * 30.0,
                                    'number_of_hours': 0.0,
                                    'amount': amount,
                                    'type': 'termination'}
                            line_ids.append(vals)
                sum_days = 0
                for rec in termination.employee_id.holidays_balance:
                    sum_days += rec.holidays_available_stock
                # 2) الإجازة
                if sum_days >= termination.termination_type_id.max_days and not termination.termination_type_id.all_holidays:
                    sum_days = termination.termination_type_id.max_days
                if sum_days > 0:
                    if grid_id:
                        amount = (basic_salary / 30.0) * sum_days
                        if amount != 0.0:
                            vals = {'name': termination.termination_type_id.name + " " + u'رصيد إجازة' + name,
                                    'employee_id': termination.employee_id.id,
                                    'number_of_days': sum_days,
                                    'number_of_hours': 0.0,
                                    'amount': amount,
                                    'type': 'termination'}
                            line_ids.append(vals)
        return line_ids

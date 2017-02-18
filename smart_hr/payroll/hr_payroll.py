# -*- coding: utf-8 -*-


from openerp import models, fields, api, tools, _
import openerp.addons.decimal_precision as dp
from datetime import datetime
from datetime import timedelta
from openerp.addons.smart_base.util.umalqurra import *
from umalqurra.hijri_date import HijriDate
from umalqurra.hijri import Umalqurra
from tempfile import TemporaryFile
import base64


class HrPayslipRun(models.Model):
    _name = 'hr.payslip.run'
    _inherit = ['hr.payslip.run', 'mail.thread']

    @api.multi
    def get_default_month(self):
        return get_current_month_hijri(HijriDate)

    month = fields.Selection(MONTHS, string='الشهر', required=1, readonly=1, states={'draft': [('readonly', 0)]}, default=get_default_month)
    employee_ids = fields.Many2many('hr.employee', string='الموظفين', readonly=1, states={'draft': [('readonly', 0)]})
    state = fields.Selection([('draft', 'مسودة'),
                              ('verify', 'في إنتظار الإعتماد'),
                              ('done', 'تم'),
                              ('cancel', 'ملغى'),
                              ('close', 'مغلق'),
                              ], 'الحالة', select=1, readonly=1, copy=False)

    @api.onchange('month')
    def onchange_month(self):
        if self.month:
            self.date_start = get_hijri_month_start(HijriDate, Umalqurra, self.month)
            self.date_end = get_hijri_month_end(HijriDate, Umalqurra, self.month)
            self.name = u'مسير جماعي  شهر %s' % self.month

    @api.one
    def action_verify(self):
        self.state = 'verify'
        for slip in self.slip_ids:
            if slip.state == 'draft':
                slip.action_verify()

    @api.one
    def action_done(self):
        self.state = 'done'
        for slip in self.slip_ids:
            slip.action_done()

    @api.one
    def action_cancel(self):
        self.state = 'cancel'
        for slip in self.slip_ids:
            slip.action_cancel()

    @api.multi
    def compute_sheet(self):
        payslip_obj = self.env['hr.payslip']
        for employee in self.employee_ids:
            payslip_val = {'employee_id': employee.id,
                           'month': self.month,
                           'name': _('راتب موظف %s لشهر %s') % (employee.name, self.month),
                           'payslip_run_id': self.id,
                           'date_from': self.date_start,
                           'date_to': self.date_end
                           }
            payslip = payslip_obj.create(payslip_val)
            payslip.onchange_employee()
            payslip.compute_sheet()


class HrPayslip(models.Model):
    _inherit = 'hr.payslip'

    @api.multi
    def get_default_month(self):
        return get_current_month_hijri(HijriDate)

    # TODO: generate التسلسل

    month = fields.Selection(MONTHS, string='الشهر', required=1, readonly=1, states={'draft': [('readonly', 0)]}, default=get_default_month)
    days_off_line_ids = fields.One2many('hr.payslip.days_off', 'payslip_id', 'الإجازات والغيابات', readonly=True, states={'draft': [('readonly', False)]})
    state = fields.Selection([('draft', 'مسودة'),
                              ('verify', 'في إنتظار الإعتماد'),
                              ('done', 'تم'),
                              ('cancel', 'ملغى'),
                              ], 'الحالة', select=1, readonly=1, copy=False)

    @api.one
    def action_verify(self):
        self.number = self.env['ir.sequence'].get('seq.hr.payslip')
        self.state = 'verify'

    @api.one
    def action_done(self):
        self.state = 'done'
        # update_loan_date
        self.env['hr.loan'].update_loan_date(self.month, self.employee_id.id)

    @api.one
    def action_cancel(self):
        self.state = 'cancel'

    @api.onchange('employee_id', 'date_from', 'date_to', 'month')
    def onchange_employee(self):
        if (not self.employee_id) or (not self.date_from) or (not self.date_to):
            return
        employee_id = self.employee_id
        self.date_from = get_hijri_month_start(HijriDate, Umalqurra, self.month)
        self.date_to = get_hijri_month_end(HijriDate, Umalqurra, self.month)
        self.name = _('راتب موظف %s لشهر %s') % (employee_id.name, self.month)
        self.company_id = employee_id.company_id
        # computation of أيام العمل
        worked_days_line_ids, leaves = self.get_worked_day_lines_without_contract(self.employee_id.id, self.employee_id.calendar_id, self.date_from, self.date_to)
        deductions = self.get_all_deduction(self.employee_id.id, self.month)
        # TODO : remove nb days deducation absence from nb worked_days
        print '-----leaves-----', leaves
        print '-----attendances-----', worked_days_line_ids
        print '-----deductions-----', deductions
        self.worked_days_line_ids = worked_days_line_ids
        self.days_off_line_ids = leaves + deductions

    def get_worked_day_lines_without_contract(self, employee_id, working_hours, date_from, date_to, compute_leave=True):
        '''
        احتساب عدد الأيام المدفوعة الأجر
        احتساب عدد أيام الإجازات
        :param employee_id:
        :param working_hours: وردية الموظف
        :param date_from:
        :param date_to:
        '''
        def employee_was_on_leave(employee_id, datetime_day, context=None):
            res = False
            day = datetime_day.strftime("%Y-%m-%d")
            # TODO: get correct state
            holiday_ids = self.env['hr.holidays'].search([('state', 'in', ('validate', 'done')),
                                                          ('employee_id', '=', employee_id),
                                                          ('type', '=', 'remove'),
                                                          ('date_from', '<=', day),
                                                          ('date_to', '>=', day)])
            if holiday_ids:
                res = holiday_ids[0].holiday_status_id.name
            return res

        leaves = {}
        attendances = {'name': _(u"عدد أيام العمل المدفوعة الأجر 100%"),
                       'sequence': 1,
                       'code': 'WORK100',
                       'number_of_days': 0.0,
                       'number_of_hours': 0.0,
                       'contract_id': False}
        day_from = datetime.strptime(date_from, "%Y-%m-%d")
        day_to = datetime.strptime(date_to, "%Y-%m-%d")
        nb_of_days = (day_to - day_from).days + 1
        for day in range(0, nb_of_days):
            working_hours_on_day = self.env['resource.calendar'].working_hours_on_day(working_hours, day_from + timedelta(days=day))
            if working_hours_on_day:
                # the employee had to work
                leave_type = employee_was_on_leave(employee_id, day_from + timedelta(days=day))
                if leave_type and compute_leave:
                    # if he was on leave, fill the leaves dict
                    if leave_type in leaves:
                        leaves[leave_type]['number_of_days'] += 1.0
                        leaves[leave_type]['number_of_hours'] += working_hours_on_day
                    else:
                        leaves[leave_type] = {
                            'name': leave_type,
                            'sequence': 5,
                            'code': leave_type,
                            'number_of_days': 1.0,
                            'number_of_hours': working_hours_on_day,
                            'contract_id': False,
                            'type': 'holiday',
                        }
                else:
                    # add the input vals to tmp (increment if existing)
                    attendances['number_of_days'] += 1.0
                    attendances['number_of_hours'] += working_hours_on_day
        leaves = [value for key, value in leaves.items()]
        return [attendances], leaves

    def get_all_deduction(self, employee_id, month):
        '''
        احتساب عدد الأيام الحسميات
        :param employee_id:
        :param month:
        '''
        deduction_ids = self.env['hr.deduction.line'].search([('state', '=', 'waiting'),
                                                              ('employee_id', '=', employee_id),
                                                              ('month', '=', month)])
        print '--deduction_ids----', deduction_ids
        # deduction_type
        deductions = {}
        for deduction in deduction_ids:
            if deduction.deduction_type_id.id in deductions:
                deductions[deduction.deduction_type_id.id]['number_of_days'] += deduction.amount
            else:
                deductions[deduction.deduction_type_id.id] = {'name': deduction.deduction_type_id.name,
                                                              'sequence': 5,
                                                              'code': deduction.deduction_type_id.id,
                                                              'number_of_days': deduction.amount,
                                                              'type': deduction.deduction_type_id.type,
                                                              # 'number_of_hours': working_hours_on_day,you can get the working_hours_on_day only for day
                                                              }
        deductions = [value for key, value in deductions.items()]
        return deductions

    def get_all_structures_for_payslip(self, cr, uid, structure_id, context):
        structure_ids = [structure_id]
        if not structure_ids:
            return []
        return list(set(self.pool.get('hr.payroll.structure')._get_parent_structure(cr, uid, structure_ids, context=context)))

    @api.multi
    def compute_sheet(self):
        print '----new compute_sheet ---------'
        salary_grid_obj = self.env['salary.grid.detail']
        bonus_line_obj = self.env['hr.bonus.line']
        loan_obj = self.env['hr.loan']
        difference_line_obj = self.env['hr.difference.line']
        for payslip in self:
            # delete old line
            payslip.line_ids.unlink()
            # generate  lines
            employee = payslip.employee_id
            ttype = employee.job_id.type_id
            grade = employee.job_id.grade_id
            degree = employee.degree_id
            # search the correct salary_grid for this employee
            salary_grids = salary_grid_obj.search([('type_id', '=', ttype.id), ('grade_id', '=', grade.id), ('degree_id', '=', degree.id)])
            if not salary_grids:
                return
            salary_grid = salary_grids[0]
            basic_salary = salary_grid.basic_salary
            # compute
            lines = []
            sequence = 1
            allowance_total = 0.0
            deduction_total = 0.0
            difference_total = 0.0
            # 1- الراتب الأساسي
            basic_salary_val = {'name': u'الراتب الأساسي',
                                'slip_id': payslip.id,
                                'employee_id': employee.id,
                                'rate': 0.0,
                                'amount': basic_salary,
                                'category': 'basic_salary',
                                'type': 'basic_salary',
                                'sequence': sequence,
                                }
            lines.append(basic_salary_val)
            # 2- البدلات القارة
            for allowance in salary_grid.allowance_ids:
                sequence += 1
                amount = allowance.get_value(employee.id)
                allowance_val = {'name': allowance.allowance_id.name,
                                 'slip_id': payslip.id,
                                 'employee_id': employee.id,
                                 'rate': 0.0,
                                 'amount': amount,
                                 'category': 'allowance',
                                 'type': 'allowance',
                                 'sequence': sequence,
                                 }
                lines.append(allowance_val)
                allowance_total += amount
            for reward in salary_grid.reward_ids:
                sequence += 1
                amount = reward.get_value(employee.id)
                reward_val = {'name': reward.reward_id.name,
                              'slip_id': payslip.id,
                              'employee_id': employee.id,
                              'rate': 0.0,
                              'amount': amount,
                              'category': 'allowance',
                              'type': 'reward',
                              'sequence': sequence,
                              }
                lines.append(reward_val)
                allowance_total += amount
            sequence += 1
            for indemnity in salary_grid.indemnity_ids:
                amount = indemnity.get_value(employee.id)
                indemnity_val = {'name': indemnity.indemnity_id.name,
                                 'slip_id': payslip.id,
                                 'employee_id': employee.id,
                                 'rate': 0.0,
                                 'amount': amount,
                                 'category': 'allowance',
                                 'type': 'indemnity',
                                 'sequence': sequence,
                                 }
                lines.append(indemnity_val)
                allowance_total += amount
                sequence += 1
            # 3- البدلات المتغيرة
            bonus_lines = bonus_line_obj.search([('employee_id', '=', employee.id), ('state', '=', 'progress'),
                                                ('month_from', '<=', payslip.month), ('month_to', '>=', payslip.month)])
            for bonus in bonus_lines:
                bonus_type = 'allowance'
                if bonus.reward_id:
                    bonus_type = 'reward'
                if bonus.indemnity_id:
                    bonus_type = 'indemnity'
                bonus_amount = bonus.get_value(employee.id)
                bonus_val = {'name': bonus.name,
                             'slip_id': payslip.id,
                             'employee_id': employee.id,
                             'rate': 0.0,
                             'amount': bonus_amount,
                             'category': 'allowance',
                             'type': bonus_type,
                             'sequence': sequence
                             }
                lines.append(bonus_val)
                allowance_total += bonus_amount
                sequence += 1
            # 4 - الفروقات
            difference_lines = difference_line_obj.search([('employee_id', '=', employee.id), ('difference_id.state', '=', 'done'), ('month', '<=', payslip.month)])
            for difference in difference_lines:
                difference_val = {'name': difference.name,
                                  'slip_id': payslip.id,
                                  'employee_id': employee.id,
                                  'rate': 0.0,
                                  'amount': difference.amount,
                                  'category': 'difference',
                                  'type': 'difference',
                                  'sequence': sequence
                                  }
                lines.append(difference_val)
                difference_total += difference.amount
                sequence += 1
            # 4- الحسميات
            deduction_retard_leave = 0.0
            deduction_absence = 0.0

            retard_leave_days = 0
            absence_days = 0
            holiday_days = 0

            for line in payslip.days_off_line_ids:
                if line.type == 'retard_leave':
                    retard_leave_days += line.number_of_days
                elif line.type == 'absence':
                    absence_days += line.number_of_days
                elif line.type == 'holiday':
                    holiday_days += line.number_of_days

            # get number of days by month
            worked_days_line_ids, leaves = self.get_worked_day_lines_without_contract(employee.id, employee.calendar_id, payslip.date_from, payslip.date_to, False)
            days_by_month = worked_days_line_ids and worked_days_line_ids[0].get('number_of_days', 22)
            # حسم‬  التأخير يكون‬ من‬  الراتب‬ الأساسي فقط
            if retard_leave_days:
                deduction_retard_leave = basic_salary / days_by_month * retard_leave_days
                retard_leave_val = {'name': u'تأخير وخروج مبكر',
                                    'slip_id': payslip.id,
                                    'employee_id': employee.id,
                                    'rate': retard_leave_days,
                                    'amount': deduction_retard_leave,
                                    'category': 'deduction',
                                    'type': 'retard_leave',
                                    'sequence': sequence
                                    }
                lines.append(retard_leave_val)
                deduction_total += deduction_retard_leave
                sequence += 1
            #  حسم‬  الغياب‬ يكون‬ من‬  جميع البدلات . و  الراتب‬ الأساسي للموظفين‬ الرسميين‬ والمستخدمين
            if absence_days:
                deduction_absence = (basic_salary + allowance_total) / days_by_month * absence_days
                retard_leave_val = {'name': u'غياب',
                                    'slip_id': payslip.id,
                                    'employee_id': employee.id,
                                    'rate': absence_days,
                                    'amount': deduction_absence,
                                    'category': 'deduction',
                                    'type': 'absence',
                                    'sequence': sequence
                                    }
                lines.append(retard_leave_val)
                deduction_total += deduction_absence
                sequence += 1
            # 5- القروض
            loans = loan_obj.get_loan_employee_month(payslip.month, employee.id)
            for loan in loans:
                loan_val = {'name': loan['name'],
                            'slip_id': payslip.id,
                            'employee_id': employee.id,
                            'rate': 0.0,
                            'amount': loan['amount'],
                            'category': 'deduction',
                            'type': 'loan',
                            'sequence': sequence
                            }
                lines.append(loan_val)
                deduction_total += loan['amount']
                sequence += 1
            # 6- التقاعد‬
            retirement_amount = (basic_salary + allowance_total - deduction_total) * salary_grid.retirement / 100.0
            retirement_val = {'name': 'التقاعد',
                              'slip_id': payslip.id,
                              'employee_id': employee.id,
                              'rate': 0.0,
                              'amount': retirement_amount,
                              'category': 'deduction',
                              'type': 'retirement',
                              'sequence': sequence}
            lines.append(retirement_val)
            deduction_total += retirement_amount
            sequence += 1
            # 7- التأمينات‬
            insurance_amount = (basic_salary + allowance_total) * salary_grid.insurance / 100.0
            insurance_val = {'name': 'التأمين',
                             'slip_id': payslip.id,
                             'employee_id': employee.id,
                             'rate': 0.0,
                             'amount': insurance_amount,
                             'category': 'deduction',
                             'type': 'insurance',
                             'sequence': sequence}
            lines.append(insurance_val)
            deduction_total += insurance_amount
            sequence += 1
            # 0- صافي الراتب
            salary_net = basic_salary + allowance_total + difference_total - deduction_total
            salary_net_val = {'name': u'صافي الراتب',
                              'slip_id': payslip.id,
                              'employee_id': employee.id,
                              'rate': 0.0,
                              'amount': salary_net,
                              'category': 'salary_net',
                              'type': 'salary_net',
                              'sequence': sequence,
                              }
            lines.append(salary_net_val)
            # print '---------------', lines
            payslip.line_ids = lines


class HrPayslipWorkedDays(models.Model):
    _inherit = 'hr.payslip.worked_days'

    # make contract_id not required
    contract_id = fields.Many2one('hr.contract', 'Contract', required=False)


class HrPayslipLine(models.Model):
    _inherit = 'hr.payslip.line'

    # make theses fields  not required
    contract_id = fields.Many2one('hr.contract', 'Contract', required=False)
    salary_rule_id = fields.Many2one('hr.salary.rule', 'Rule', required=False)
    code = fields.Char('Code', size=64, required=False)
    category_id = fields.Many2one('hr.salary.rule.category', 'Category', required=False)

    # added
    category = fields.Selection([('basic_salary', 'الراتب الأساسي'),
                                 ('allowance', 'البدلات'),
                                 ('difference', 'فروقات'),
                                 ('deduction', 'الحسميات'),
                                 ('retirement', 'التقاعد'),
                                 ('insurance', 'التأمين'),
                                 ('salary_net', 'صافي الراتب'),
                                 ], string='الفئة', select=1, readonly=1)

    type = fields.Selection([('basic_salary', 'الراتب الأساسي'),
                             ('allowance', 'البدلات'),
                             ('reward', u'المكافآت‬'),
                             ('indemnity', 'التعويضات'),
                             ('difference', 'فروقات'),
                             ('retard_leave', 'تأخير وخروج'),
                             ('absence', 'غياب'),
                             ('holiday', 'إجازة'),
                             ('loan', 'قروض'),
                             ('retirement', 'التقاعد'),
                             ('insurance', 'التأمين'),
                             ('salary_net', 'صافي الراتب'),
                             ], string='النوع', select=1, readonly=1)


class HrPayslipDaysOff(models.Model):
    _name = 'hr.payslip.days_off'
    _description = u'أيام الإجازات والغيابات'

    name = fields.Char('الوصف', required=1)
    payslip_id = fields.Many2one('hr.payslip', 'Pay Slip', required=1, ondelete='cascade', select=1)
    code = fields.Char('الرمز', required=0)
    number_of_days = fields.Float('عدد الأيام')
    number_of_hours = fields.Float('عدد الساعات')
    type = fields.Selection([('retard_leave', 'تأخير وخروج'), ('absence', 'غياب'), ('holiday', 'إجازة')], string='النوع', required=1)


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'
    _order = 'sequence'

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
from openerp.exceptions import UserError
from openerp.exceptions import ValidationError


class HrPayslipRun(models.Model):
    _name = 'hr.payslip.run'
    _inherit = ['hr.payslip.run', 'mail.thread']

    @api.multi
    def get_default_month(self):
        return get_current_month_hijri(HijriDate)

    @api.one
    @api.depends('slip_ids.salary_net')
    def _amount_all(self):
        amount_total = 0.0
        for line in self.slip_ids:
            amount_total += line.salary_net
        self.amount_total = amount_total

    month = fields.Selection(MONTHS, string='الشهر', required=1, readonly=1, states={'draft': [('readonly', 0)]}, default=get_default_month)
    employee_ids = fields.Many2many('hr.employee', string='الموظفين', readonly=1, states={'draft': [('readonly', 0)]})
    state = fields.Selection([('draft', 'مسودة'),
                              ('verify', 'في إنتظار الإعتماد'),
                              ('done', 'تم'),
                              ('cancel', 'ملغى'),
                              ('close', 'مغلق'),
                              ], 'الحالة', select=1, readonly=1, copy=False)

    amount_total = fields.Float(string='الإجمالي', store=True, readonly=True, compute='_amount_all')
    bank_file = fields.Binary(string='الملف البنكي', attachment=True)
    bank_file_name = fields.Char(string='مسمى الملف البنكي')
    department_level1_id = fields.Many2one('hr.department', string='الفرع', readonly=1, states={'draft': [('readonly', 0)]})
    department_level2_id = fields.Many2one('hr.department', string='القسم', readonly=1, states={'draft': [('readonly', 0)]})
    department_level3_id = fields.Many2one('hr.department', string='الشعبة', readonly=1, states={'draft': [('readonly', 0)]})
    salary_grid_type_id = fields.Many2one('salary.grid.type', string='الصنف', readonly=1, states={'draft': [('readonly', 0)]},)

    @api.onchange('month')
    def onchange_month(self):
        if self.month:
            um = HijriDate.today()
            if int(um.month) < int(self.month):
                raise UserError(u"لا يمكن انشاء مسير لشهر في المستقبل ")
            self.date_start = get_hijri_month_start(HijriDate, Umalqurra, self.month)
            self.date_end = get_hijri_month_end(HijriDate, Umalqurra, self.month)
            self.name = u'مسير جماعي  شهر %s' % self.month

    @api.onchange('department_level1_id', 'department_level2_id', 'department_level3_id', 'salary_grid_type_id')
    def onchange_department_level(self):
        dapartment_obj = self.env['hr.department']
        employee_obj = self.env['hr.employee']
        department_level1_id = self.department_level1_id and self.department_level1_id.id or False
        department_level2_id = self.department_level2_id and self.department_level2_id.id or False
        department_level3_id = self.department_level3_id and self.department_level3_id.id or False
        employee_ids = []
        dapartment_id = False
        if department_level3_id:
            dapartment_id = department_level3_id
        elif department_level2_id:
            dapartment_id = department_level2_id
        elif department_level1_id:
            dapartment_id = department_level1_id
        if dapartment_id:
            dapartment = dapartment_obj.browse(dapartment_id)
            employee_ids += [x.id for x in dapartment.member_ids]
            for child in dapartment.all_child_ids:
                employee_ids += [x.id for x in child.member_ids]
        result = {}
        if not employee_ids:
            # get all employee
            employee_ids = employee_obj.search([('employee_state', '=', 'employee')]).ids
        # filter by type
        if self.salary_grid_type_id:
            employee_ids = employee_obj.search([('id', 'in', employee_ids), ('type_id', '=', self.salary_grid_type_id.id)]).ids
        result.update({'domain': {'employee_ids': [('id', 'in', list(set(employee_ids)))]}})
        return result

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
        self.generate_file()

    @api.one
    def button_refuse(self):
        self.state = 'cancel'
        for slip in self.slip_ids:
            slip.action_cancel()

    @api.multi
    def compute_sheet(self):
        payslip_obj = self.env['hr.payslip']
        for employee in self.employee_ids:
            payslip_val = {'employee_id': employee.id,
                           'month': self.month,
                           'name': _('راتب موظف %s لشهر %s') % (employee.display_name, self.month),
                           'payslip_run_id': self.id,
                           'date_from': self.date_start,
                           'date_to': self.date_end
                           }
            payslip = payslip_obj.create(payslip_val)
            payslip.onchange_employee()
            payslip.compute_sheet()

    @api.multi
    def generate_file(self):
        # TODO: must check all fields
        fp = TemporaryFile()
        header_key = '000000000000'
        calendar_type = 'H'
        current_date = HijriDate.today()
        year = str(int(current_date.year)).zfill(4)
        month = str(int(current_date.month)).zfill(2)
        day = str(int(current_date.day)).zfill(2)
        send_date = year + month + day
        value_date = send_date  # TODO: the ValueDate
        total_amount = str(self.amount_total).replace('.', '').replace(',', '').zfill(15)
        total_employees = str(len(self.slip_ids)).zfill(8)
        account_number = str(self.env.user.company_id.vat or '').zfill(13)
        file_parameter = '1'
        file_sequence = '01'
        filler = ''.rjust(65, ' ')
        file_dec = ''
        file_dec += u'%s%s%s%s%s%s%s%s%s%s\n' % (header_key, calendar_type, send_date, value_date, total_amount, total_employees, account_number, file_parameter, file_sequence, filler)
        for playslip in self.slip_ids:
            employee = playslip.employee_id
            # add line for each playslip
            employee_number = employee.number.ljust(12, ' ')
            # search account bank for this employee
            banks = self.env['res.partner.bank'].search([('employee_id', '=', employee.id), ('is_deposit', '=', True)])
            if not banks:
                raise UserError(u"يجب إنشاء حساب بنكي للإيداع  للموظف  %s " % employee.display_name)
            employee_bank = banks[0]
            employee_bank_id = employee_bank.bank_id.bic.ljust(4, ' ')
            employee_account_number = employee_bank.acc_number.ljust(24, ' ')
            employee_name = '*****'.ljust(50, ' ')
            employee_amount = str(playslip.salary_net).replace('.', '').replace(',', '').zfill(15)
            civilian_id = employee.identification_id.zfill(15)
            employee_id_type = '0'
            process_flag = ' '
            block_amount = ' '
            kawadar_flag = ' '
            filler = ''.rjust(11, ' ')
            file_dec += u'%s%s%s%s%s%s%s%s%s%s%s\n' % (employee_number, employee_bank_id, employee_account_number, employee_name, employee_amount, civilian_id, employee_id_type, process_flag, block_amount, kawadar_flag, filler)
        # remove the \n
        file_dec = file_dec[0:len(file_dec) - 1]
        fp.write(file_dec.encode('utf-8'))
        fp.seek(0)
        bank_file_name = u'مسير جماعي  شهر %s.%s' % (self.month, 'txt')
        self.bank_file = base64.encodestring(fp.read())
        self.bank_file_name = bank_file_name
        fp.close()
        return True


class HrPayslipDifferenceHistory(models.Model):
    _name = 'hr.payslip.difference.history'
    _description = 'الفروقات المتخلدة'

    payslip_id = fields.Many2one('hr.payslip', 'Pay Slip', required=1, ondelete='cascade', select=1)
    employee_id = fields.Many2one('hr.employee', string=u'الموظف')
    month = fields.Integer(string=u'الشهر')
    amount = fields.Float(string=u'المبلغ المتخلد')


class HrPayslip(models.Model):
    _name = 'hr.payslip'
    _inherit = ['hr.payslip', 'mail.thread']
    _order = 'date_from desc,id desc'

    @api.multi
    def get_default_month(self):
        return get_current_month_hijri(HijriDate)

    month = fields.Selection(MONTHS, string='الشهر', required=1, readonly=1, states={'draft': [('readonly', 0)]}, default=get_default_month)
    days_off_line_ids = fields.One2many('hr.payslip.days_off', 'payslip_id', 'الإجازات والغيابات', readonly=True, states={'draft': [('readonly', False)]})
    salary_net = fields.Float(string='صافي الراتب')
    difference_history_ids = fields.One2many('hr.payslip.difference.history', 'payslip_id', 'الفروقات المتخلدة')
    state = fields.Selection([('draft', 'مسودة'),
                              ('verify', 'في إنتظار الإعتماد'),
                              ('done', 'تم'),
                              ('cancel', 'ملغى'),
                              ], 'الحالة', select=1, readonly=1, copy=False)
    with_advanced_salary = fields.Boolean(string=u"مع صرف راتب مسبق", default=False, readonly=1)
    grade_id = fields.Many2one('salary.grid.grade', string=u'المرتبة')
    degree_id = fields.Many2one('salary.grid.degree', string=u'الدرجة')
    type_id = fields.Many2one('salary.grid.type', string=u'صنف الموظف')

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
    def button_refuse(self):
        self.state = 'cancel'

    @api.multi
    @api.onchange('employee_id', 'month')
    def _onchange_employee_id(self):
        # check the existance of difference and dedections for current month
        self.date_from = get_hijri_month_start(HijriDate, Umalqurra, self.month)
        self.date_to = get_hijri_month_end(HijriDate, Umalqurra, self.month)
#         if self.env['hr.difference'].search_count([('date_from', '=', self.date_from), ('date_to', '=', self.date_to), ('state', '=', 'done')]) == 0:
#             raise ValidationError(u"لم يتم إحتساب الفروقات لهذا الشهر")
#         if self.env['hr.deduction'].search_count([('date_from', '=', self.date_from), ('date_to', '=', self.date_to), ('state', '=', 'done')]) == 0:
#             raise ValidationError(u"لم يتم إحتساب الحسميات لهذا الشهر")
        if not self.employee_id and self.month:
            res = {}
            employee_ids = self.env['hr.employee'].search([('employee_state', '=', 'employee')])
            employee_ids = employee_ids.ids
            termination_ids = self.env['hr.termination'].search([('state', '=', 'done')], order='date_termination desc', limit=1)
            minus_employee_ids = []
            for termination_id in termination_ids:
                if termination_id.date_termination and fields.Date.from_string(termination_id.date_termination) < fields.Date.from_string(self.date_from):
                    minus_employee_ids.append(termination_id.employee_id)
            minus_employee_ids = [rec.id for rec in minus_employee_ids]
            result_employee_ids = list((set(employee_ids) - set(minus_employee_ids)))
            res['domain'] = {'employee_id': [('id', 'in', result_employee_ids)]}
            return res
#         res = {}
#         if self.type_appointment and self.type_appointment.for_members is True:
#             employee_ids = self.env['hr.employee'].search(
#                 [('is_member', '=', True), ('employee_state', 'in', ['done', 'employee'])])
#             job_ids = self.env['hr.job'].search([('name.members_job', '=', True),('state','=', 'unoccupied'),('type_id.is_member','=',True)])
#             print"job_ids",job_ids
#             res['domain'] = {'employee_id': [('id', 'in', employee_ids.ids)], 'job_id': [('id', 'in', job_ids.ids)]}
#             return res
#         if self.type_appointment and self.type_appointment.for_members is False:
#             employee_ids = self.env['hr.employee'].search(
#                 [('is_member', '=', False), ('employee_state', 'in', ['done', 'employee'])])
#             job_ids = self.env['hr.job'].search([('name.members_job', '=', False),('state','=', 'unoccupied')])
#             res['domain'] = {'employee_id': [('id', 'in', employee_ids.ids)], 'job_id': [('id', 'in', job_ids.ids)]}
#             return res

    @api.onchange('employee_id', 'date_from', 'date_to', 'month')
    def onchange_employee(self):
        if (not self.employee_id) or (not self.date_from) or (not self.date_to):
            return
        employee_id = self.employee_id
        self.date_from = get_hijri_month_start(HijriDate, Umalqurra, self.month)
        self.date_to = get_hijri_month_end(HijriDate, Umalqurra, self.month)
        self.name = _('راتب موظف %s لشهر %s') % (employee_id.name, self.month)
        self.company_id = employee_id.company_id
        print 'self.employee_id.grade_id', self.employee_id.grade_id.id
        self.grade_id = self.employee_id.grade_id.id
        self.degree_id = self.employee_id.degree_id.id
        self.type_id = self.employee_id.type_id.id
        # computation of أيام العمل
        worked_days_line_ids, leaves = self.get_worked_day_lines_without_contract(self.employee_id.id, self.employee_id.calendar_id, self.date_from, self.date_to)
        deductions = self.get_all_deduction(self.employee_id.id, self.month)
        # TODO : remove nb days deducation absence from nb worked_days
        self.worked_days_line_ids = worked_days_line_ids
        self.days_off_line_ids = leaves + deductions

    def get_worked_day_lines_without_contract(self, employee_id, working_hours, date_from, date_to, compute_leave=True):
        """

 احتساب عدد الأيام المدفوعة الأجر
احتساب عدد أيام الإجازات
        :param employee_id:
        :param working_hours: وردية الموظف
        :param date_from:
        :param date_to:
        """
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
        """
   احتساب عدد الأيام الحسميات
        :param employee_id:
        :param month:
        """
        deduction_ids = self.env['hr.deduction.line'].search([('state', '=', 'waiting'),
                                                              ('employee_id', '=', employee_id),
                                                              ('month', '=', month)])
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
        # amount_multiplication is 1 normale payslip generation
        # amount_multiplication will be 2 if self.with_advanced_salary is true;
        # amount_multiplication will be 0 if current payslip's salary grid is allready generated for the previous month's payslip ;
        amount_multiplication = 1
        # check weither the employee is terminated
        # TODO: must remove this message raise !
        # if self.employee_id.emp_state == 'terminated':
        # termination_id = self.env['hr.termination'].search([('employee_id', '=', self.employee_id.id), ('state', '=', 'done')], order='date_termination desc', limit=1)
        # if fields.Date.from_string(termination_id.date_termination) < fields.Date.from_string(self.date_from) or fields.Date.from_string(termination_id.date_termination) > fields.Date.from_string(self.date_to):
        # raise UserError(u"لقد تم طي قيد %s " % self.employee_id.name)
        # check if the salary is allready given in the last payslip for the previous month
        previous_month_payslip = False
        if self.month != '01':
            # previous month in current year
            previous_month = '0' + str((int(self.month) - 1))
            current_year_date = str(fields.Date.from_string(self.date_from).year) + '-01-01'
            current_year_date = fields.Date.from_string(current_year_date)
            previous_month_payslip = self.env['hr.payslip'].search_count([('date_from', '>=', current_year_date),
                                                                          ('employee_id', '=', self.employee_id.id),
                                                                          ('month', '=', previous_month),
                                                                          ('with_advanced_salary', '=', True),
                                                                          ('state', '=', 'done')
                                                                          ])
        else:
            # previous month in previous year
            previous_month = '0' + str((int(self.month) - 1))
            previous_year_date = str(fields.Date.from_string(self.date_from).year - 1) + '-12-31'
            previous_year_date = fields.Date.from_string(previous_year_date)
            previous_month_payslip = self.env['hr.payslip'].search_count([('date_to', '<=', previous_year_date),
                                                                          ('employee_id', '=', self.employee_id.id),
                                                                          ('month', '=', previous_month),
                                                                          ('with_advanced_salary', '=', True),
                                                                          ('state', '=', 'done')
                                                                          ])
        if previous_month_payslip > 0:
            # the employee is allready have the salary_grid of the current month
            amount_multiplication = 0
        # check if the employee need an advanced salary from the holidays
        holidays_ids = self.env['hr.holidays'].search([('date_to', '>=', self.date_from),
                                                       ('date_to', '<=', self.date_to),
                                                       ('employee_id', '=', self.employee_id.id),
                                                       ('state', '=', 'done')
                                                       ])
        for holiday_id in holidays_ids:
            if holiday_id.with_advanced_salary:
                self.with_advanced_salary = True
                amount_multiplication = 2
                break
        bonus_line_obj = self.env['hr.bonus.line']
        loan_obj = self.env['hr.loan']
        difference_line_obj = self.env['hr.difference.line']
        for payslip in self:
            # delete old line
            payslip.line_ids.unlink()
            # delete old difference_history
            payslip.difference_history_ids.unlink()
            # generate  lines
            employee = payslip.employee_id
            # search the newest salary_grid for this employee
            salary_grid, basic_salary = employee.get_salary_grid_id(False)
            if not salary_grid:
                return
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
                                'amount': basic_salary * amount_multiplication,
                                'category': 'basic_salary',
                                'type': 'basic_salary',
                                'sequence': sequence,
                                }
            lines.append(basic_salary_val)
            # 2- البدلات القارة
            for allowance in salary_grid.allowance_ids:
                sequence += 1
                amount = allowance.get_value(employee.id) * amount_multiplication
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
                amount = reward.get_value(employee.id) * amount_multiplication
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
                amount = indemnity.get_value(employee.id) * amount_multiplication
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
                if bonus.increase_id:
                    bonus_type = 'increase'
                bonus_amount = bonus.get_value(employee.id)
                bonus_val = {'name': bonus.name,
                             'slip_id': payslip.id,
                             'employee_id': employee.id,
                             'rate': 0.0,
                             'amount': bonus_amount,
                             'category': 'changing_allowance',
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
            retard_leave_days = 0
            absence_days = 0
            holiday_days = 0
            sanction_days = 0

            for line in payslip.days_off_line_ids:
                if line.type == 'retard_leave':
                    retard_leave_days += line.number_of_days
                elif line.type == 'absence':
                    absence_days += line.number_of_days
                elif line.type == 'holiday':
                    holiday_days += line.number_of_days
                elif line.type == 'sanction':
                    sanction_days += line.number_of_days

            # حسم‬  التأخير يكون‬ من‬  الراتب‬ الأساسي فقط
            if retard_leave_days:
                # احتساب الحسم يقسم الراتب على 30
                deduction_retard_leave = basic_salary / 30.0 * retard_leave_days
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
                # احتساب الحسم يقسم الراتب على 30
                deduction_absence = (basic_salary + allowance_total) / 30.0 * absence_days
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
            # عقوبة
            if sanction_days:
                # احتساب الحسم يقسم الراتب على 30
                deduction_sanction = (basic_salary + allowance_total) / 30.0 * sanction_days
                sanction_val = {'name': u'عقوبة',
                                'slip_id': payslip.id,
                                'employee_id': employee.id,
                                'rate': sanction_days,
                                'amount': deduction_sanction,
                                'category': 'deduction',
                                'type': 'sanction',
                                'sequence': sequence
                                }
                lines.append(sanction_val)
                deduction_total += deduction_sanction
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
            # check if deduction_total is > than 1/3 of basic salary
            if deduction_total > basic_salary / 3:
                vals = {'name': 'فرق الحسميات أكثر من ثلث الراتب',
                        'slip_id': payslip.id,
                        'employee_id': employee.id,
                        'rate': 0.0,
                        'amount': deduction_total - basic_salary / 3,
                        'category': 'deduction',
                        'type': 'difference',
                        'sequence': sequence
                        }
                lines.append(vals)
                deduction_total -= basic_salary / 3
                sequence += 1
                # save the rest for the next month
                month = fields.Date.from_string(self.date_from).month + 1
                if month > 12:
                    month = 1
                self.env['hr.payslip.difference.history'].create({'payslip_id': self.id,
                                                                  'amount': deduction_total - basic_salary / 3,
                                                                  'employee_id': employee.id,
                                                                  'month': month,
                                                                  })
            # 6- التقاعد‬
            # old : retirement_amount = (basic_salary * amount_multiplication + allowance_total - deduction_total) * salary_grid.retirement / 100.0
            retirement_amount = (basic_salary * amount_multiplication) * salary_grid.retirement / 100.0
            if retirement_amount:
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
            # old insurance_amount = (basic_salary * amount_multiplication + allowance_total) * salary_grid.insurance / 100.0
            insurance_amount = (basic_salary * amount_multiplication) * salary_grid.insurance / 100.0
            if insurance_amount:
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
            salary_net = basic_salary * amount_multiplication + allowance_total + difference_total - deduction_total
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
            payslip.salary_net = salary_net
            payslip.line_ids = lines

    @api.one
    @api.constrains('employee_id', 'month')
    def _check_payroll(self):
        for rec in self:
            payroll_count = rec.search_count([('employee_id', '=', rec.employee_id.id), ('month', '=', rec.month), ('is_special', '=', False)])
            if payroll_count > 1:
                raise ValidationError(u"لا يمكن إنشاء مسيرين لنفس الموظف في نفس الشهر")

    @api.onchange('month')
    def onchange_month(self):
        if self.month:
            um = HijriDate.today()
            if int(um.month) < int(self.month):
                raise UserError(u"لا يمكن انشاء مسير لشهر في المستقبل ")


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
                                 ('changing_allowance', 'البدلات المتغيرة'),
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
                             ('increase', 'العلاوات'),
                             ('difference', 'فروقات'),
                             ('retard_leave', 'تأخير وخروج'),
                             ('absence', 'غياب'),
                             ('holiday', 'إجازة'),
                             ('loan', 'قروض'),
                             ('retirement', 'التقاعد'),
                             ('insurance', 'التأمين'),
                             ('salary_net', 'صافي الراتب'),
                             ('sanction', 'عقوبة')
                             ], string='النوع', select=1, readonly=1)


class HrPayslipDaysOff(models.Model):
    _name = 'hr.payslip.days_off'
    _description = u'أيام الإجازات والغيابات'

    name = fields.Char('الوصف', required=1)
    payslip_id = fields.Many2one('hr.payslip', 'Pay Slip', required=1, ondelete='cascade', select=1)
    code = fields.Char('الرمز', required=0)
    number_of_days = fields.Float('عدد الأيام')
    number_of_hours = fields.Float('عدد الساعات')
    type = fields.Selection([('retard_leave', 'تأخير وخروج'), ('absence', 'غياب'), ('holiday', 'إجازة'), ('sanction', 'عقوبة')], string='النوع', required=1)


class HrSalaryRule(models.Model):
    _inherit = 'hr.salary.rule'
    _order = 'sequence'

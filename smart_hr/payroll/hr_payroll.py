# -*- coding: utf-8 -*-


from openerp import models, fields, api, tools, _
from dateutil.relativedelta import relativedelta
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
    def get_default_period_id(self):
        month = get_current_month_hijri(HijriDate)
        date = get_hijri_month_start(HijriDate, Umalqurra, int(month))
        period_id = self.env['hr.period'].search([('date_start', '<=', date),('date_stop', '>=', date)])
        return period_id

    @api.one
    @api.depends('slip_ids.salary_net')
    def _amount_all(self):
        amount_total = 0.0
        for line in self.slip_ids:
            amount_total += line.salary_net
        self.amount_total = amount_total

    period_id = fields.Many2one('hr.period', string=u'الفترة', domain=[('is_open', '=', True)], default=get_default_period_id, required=1, readonly=1, states={'draft': [('readonly', 0)]})
    employee_ids = fields.Many2many('hr.employee', string='الموظفين', readonly=1, states={'draft': [('readonly', 0)]})
    state = fields.Selection([('draft', 'إعداد الرواتب'),
                              ('verify', 'مرحل'),
                              ('finance', 'وزارة المالية'),
                              ('banking', 'إعداد الملف البنكي'),
                              ('done', 'تم صرف الرواتب'),
                              ('cancel', 'ملغى'),
                              ('close', 'مغلق'),
                              ], 'الحالة', select=1, readonly=1, copy=False)

    amount_total = fields.Float(string='الإجمالي', store=True, readonly=True, compute='_amount_all')
    error_ids = fields.One2many('hr.payslip.run.error', 'payslip_run_id', string='تقرير الموظفين المسثنين من المسير الجماعي', readonly=1)
    count_slip_ids = fields.Integer(string='count slip ids')

    slip_no_zero_ids = fields.One2many('hr.payslip', 'payslip_run_id', string='Payslips', domain=[('salary_net', '!=', 0.0)],
                                       readonly=True, states={'draft': [('readonly', False)]})

    slip_zero_ids = fields.One2many('hr.payslip', 'payslip_run_id', string='Payslips With Zero Net', domain=[('salary_net', '=', False)],
                                    readonly=True, states={'draft': [('readonly', False)]})
    # fields used to generate bank file
    bank_file = fields.Binary(string='الملف البنكي', attachment=True)
    bank_file_name = fields.Char(string='مسمى الملف البنكي')
    # fields used for filter
    department_level1_id = fields.Many2one('hr.department', string='الفرع', readonly=1, states={'draft': [('readonly', 0)]})
    department_level2_id = fields.Many2one('hr.department', string='القسم', readonly=1, states={'draft': [('readonly', 0)]})
    department_level3_id = fields.Many2one('hr.department', string='الشعبة', readonly=1, states={'draft': [('readonly', 0)]})
    salary_grid_type_id = fields.Many2many('salary.grid.type', string='الأصناف', readonly=1, states={'draft': [('readonly', 0)]})

    @api.onchange('period_id')
    def onchange_period_id(self):
        if self.period_id:
            self.date_start = self.period_id.date_start
            self.date_end = self.period_id.date_stop
            self.name = u'مسير جماعي  شهر %s' % self.period_id.name

    def compute_employee_ids(self, with_error=True):
        self.employee_ids = False
        dapartment_obj = self.env['hr.department']
        employee_obj = self.env['hr.employee']
        department_level1_id = self.department_level1_id and self.department_level1_id.id or False
        department_level2_id = self.department_level2_id and self.department_level2_id.id or False
        department_level3_id = self.department_level3_id and self.department_level3_id.id or False
        employee_ids = []
        employee_error_ids = []
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
        if not employee_ids:
            # get all employee
            employee_ids = employee_obj.search([('employee_state', '=', 'employee')]).ids
        # filter by type
        if self.salary_grid_type_id:
            employee_ids = employee_obj.search([('id', 'in', employee_ids), ('type_id', 'in', self.salary_grid_type_id.ids)]).ids
        # minus uncounted employees
        if with_error:
            self.compute_error()
            employee_error_ids = [line.employee_id.id for line in self.error_ids]
        self.employee_ids = list((set(employee_ids) - set(employee_error_ids)))

    @api.one
    def action_verify(self):
        self.state = 'verify'
        for slip in self.slip_ids:
            if slip.state == 'draft':
                slip.action_verify()

    @api.one
    def refuse_action_verify(self):
        self.state = 'verify'
        for slip in self.slip_ids:
            slip.action_verify()

    @api.one
    def action_draft(self):
        self.state = 'draft'
        for slip in self.slip_ids:
            slip.state = 'draft'

    @api.one
    def action_finance(self):
        self.state = 'finance'

    @api.one
    def action_banking(self):
        self.state = 'banking'
        self.generate_file()

    @api.one
    def action_done(self):
        self.state = 'done'
        for slip in self.slip_ids:
            slip.action_done()

    @api.one
    def button_refuse(self):
        self.state = 'cancel'
        for slip in self.slip_ids:
            slip.action_cancel()

    @api.multi
    def compute_sheet(self):
        self.slip_ids.unlink()
        self.count_slip_ids = 0
        self.compute_employee_ids()
        slip_ids = []
        for employee in self.employee_ids:
            payslip_val = {'employee_id': employee.id,
                           'period_id': self.period_id.id,
                           'name': _('راتب موظف %s لشهر %s') % (employee.display_name, self.period_id.name),
                           'payslip_run_id': self.id,
                           'date_from': self.date_start,
                           'date_to': self.date_end,
                           'grade_id': employee.grade_id.id,
                           'degree_id': employee.degree_id.id,
                           'type_id': employee.type_id.id
                           }
            slip_ids.append(payslip_val)

        self.slip_ids = slip_ids
        self.slip_ids.compute_sheet()
        self.count_slip_ids = len(self.slip_ids)

    @api.multi
    def compute_error(self):
        self.error_ids.unlink()
        error_ids = []
        #  موظفين صرفت لهم إجازة مدفوعة الأجر :
        special_payslips = self.env['hr.payslip'].search([('state', '=', 'done'), ('payslip_type', '=', 'holidays'),('salary_net', '!=', 0.0),
                                                          ('period_ids', 'in', [self.period_id.id])])
        for payslip in special_payslips:
            error_ids.append({'payslip_run_id': self.id, 'employee_id': payslip.employee_id.id, 'type': 'prepaid_holiday'})

        # موظفين:  تم إيقاف راتبهم
        employee_stop_lines = self.env['hr.payslip.stop.line'].search(
            [('stop_period', '=', True), ('period_id', '=', self.period_id.id), ('payslip_id.state', '=', 'done')])
        employee_stop_ids = [line.payslip_id.employee_id.id for line in employee_stop_lines]
        for employee_id in employee_stop_ids:
            error_ids.append({'payslip_run_id': self.id, 'employee_id': employee_id, 'type': 'stop'})
        # الموظفين الذين تم إعداد مسير إفرادي لهم
        employee_payslip_lines = self.env['hr.payslip'].search([('period_id', '=', self.period_id.id), ('is_special', '=', False)])
        employee_have_payslip_ids = [payslip.employee_id.id for payslip in employee_payslip_lines]
        for employee_id in employee_have_payslip_ids:
            error_ids.append({'payslip_run_id': self.id, 'employee_id': employee_id, 'type': 'have_payslip'})
        self.error_ids = error_ids
        return True

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
        today = fields.Date.from_string(fields.Date.today())
        value_date_g = today + relativedelta(days=14)
        hijri_date = HijriDate(value_date_g.year, value_date_g.month, value_date_g.day, gr=True)
        value_date = str(int(hijri_date.year)).zfill(4) + str(int(hijri_date.month)).zfill(2) + str(int(hijri_date.day)).zfill(2)
        total_amount = str(self.amount_total).replace('.', '').replace(',', '').zfill(15)
        total_employees = str(len(self.slip_ids)).zfill(8)
        account_number = str(self.env.user.company_id.vat or '').zfill(13)
        file_parameter = '1'
        file_sequence = '01'
        filler = ''.rjust(65, ' ')
        file_dec = ''
        file_dec += u'%s%s%s%s%s%s%s%s%s%s\n' % (header_key, calendar_type, send_date, value_date, total_amount, total_employees, account_number, file_parameter, file_sequence, filler)
        for playslip in self.slip_no_zero_ids:
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
            civilian_id = employee.identification_id and employee.identification_id.zfill(15) or ''.zfill(15)
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
        bank_file_name = u'مسير جماعي  شهر %s.%s' % (self.period_id.name, 'txt')
        self.bank_file = base64.encodestring(fp.read())
        self.bank_file_name = bank_file_name
        fp.close()
        return True

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft':
                raise ValidationError(u'لا يمكن حذف مسير جماعي فى هذه المرحلة يرجى مراجعة مدير النظام')
        return super(HrPayslipRun, self).unlink()


class HrPayslipDifferenceHistory(models.Model):
    _name = 'hr.payslip.difference.history'
    _description = 'الفروقات المتخلدة'

    payslip_id = fields.Many2one('hr.payslip', string=u'المسير', required=1, ondelete='cascade', select=1)
    period_id = fields.Many2one('hr.period', string=u'الشهر')
    amount = fields.Float(string=u'المبلغ المتخلد')
    name = fields.Selection([('third_salary', u'فرق حسميات أكثر من ثلث الراتب'),
                             ('negative_salary', u'المبلغ المؤجل (سبب راتب سالب)'),
                             ], 'الفرق المتخلدة', select=1, readonly=1, copy=False)


class HrPayslip(models.Model):
    _name = 'hr.payslip'
    _inherit = ['hr.payslip', 'mail.thread']
    _order = 'date_from desc,id desc'

    @api.multi
    def get_default_period_id(self):
        month = get_current_month_hijri(HijriDate)
        date = get_hijri_month_start(HijriDate, Umalqurra, int(month))
        period_id = self.env['hr.period'].search([('date_start', '<=', date),
                                                  ('date_stop', '>=', date),
                                                  ]
                                                 )
        return period_id
    period_id = fields.Many2one('hr.period', string=u'الفترة', domain=[('is_open', '=', True)], readonly=1, required=1, states={'draft': [('readonly', 0)]}, default=get_default_period_id)
    days_off_line_ids = fields.One2many('hr.payslip.days_off', 'payslip_id', 'الإجازات والغيابات', readonly=True, states={'draft': [('readonly', False)]})
    difference_history_ids = fields.One2many('hr.payslip.difference.history', 'payslip_id', 'الفروقات المتخلدة')
    state = fields.Selection([('draft', 'إعداد'),
                              ('verify', 'مرحل'),
                              ('done', 'تم صرف الراتب'),
                              ('cancel', 'ملغى'),
                              ], 'الحالة', select=1, readonly=1, copy=False)
    grade_id = fields.Many2one('salary.grid.grade', string=u'المرتبة')
    degree_id = fields.Many2one('salary.grid.degree', string=u'الدرجة')
    type_id = fields.Many2one('salary.grid.type', string=u'صنف الموظف')
    number_of_days = fields.Integer(string=u'عدد أيام العمل', readonly=1)
    compute_date = fields.Date(string=u'تاريخ الإعداد')
    salary_net = fields.Float(string='صافي الراتب')
    allowance_total = fields.Float(string='مجموع البدلات')
    across_loan = fields.Float(string='تجاوز  قروض هذا الشهر')
    difference_deduction_total = fields.Float(string='مجموع الحسميات والفروقات')
    contraintes_ids = fields.One2many('hr.payroll.constrainte', 'payslip_id')
    operation_ids = fields.One2many('hr.payroll.operation', 'payslip_id')
    sanction_line_ids = fields.Many2many('hr.sanction.ligne')
    abscence_ids = fields.Many2many('hr.employee.absence.days')
    delays_ids = fields.Many2many('hr.employee.delay.hours')

    @api.one
    def action_verify(self):
        self.number = self.env['ir.sequence'].get('seq.hr.payslip')
        self.state = 'verify'

    @api.one
    def action_done(self):
        self.state = 'done'
        # update_loan_date
        date_start = fields.Date.from_string(self.period_id.date_start)
        date_stop = fields.Date.from_string(self.period_id.date_stop)
        self.env['hr.loan'].update_loan_date(date_start, date_stop, self.employee_id.id, self.across_loan)
        # update sanction lines
        for rec in self.sanction_line_ids:
            rec.deduction = True
        # update abscence_ids lines
        for rec in self.abscence_ids:
            rec.deduction = True
        # update delays_ids lines
        for rec in self.delays_ids:
            rec.deduction = True
        # close the financial folder of each employee who is terminated
        for rec in self.env['hr.employee'].search([('to_be_clear_financial_dues', '=', True)]):
            rec.clear_financial_dues = True

    @api.one
    def button_refuse(self):
        self.state = 'cancel'

    @api.onchange('employee_id', 'period_id')
    def onchange_employee(self):
        if self.employee_id and self.period_id:
            self.date_from = self.period_id.date_start
            self.date_to = self.period_id.date_stop
            self.name = _('راتب موظف %s لشهر %s') % (self.employee_id.display_name, self.period_id.name)
            # self.company_id = self.employee_id.company_id
            self.grade_id = self.employee_id.grade_id.id
            self.degree_id = self.employee_id.degree_id.id
            self.type_id = self.employee_id.type_id.id
            # check the existance of difference and dedections for current month
        res = {}
        employee_ids = self.env['hr.employee'].search(
            [('emp_state', 'in', ('working', 'suspended')), ('employee_state', '=', 'employee')])
        employee_ids = employee_ids.ids
        # موظفين:  طي القيد
        plus_terminated_emps = self.env['hr.employee'].search(
            [('emp_state', '=', 'terminated'), ('clear_financial_dues', '=', False)])
        if plus_terminated_emps:
            employee_ids += plus_terminated_emps.ids
        minus_employee_ids = []
        # موظفين:  تم إيقاف راتبهم
        employee_stop_lines = self.env['hr.payslip.stop.line'].search(
            [('stop_period', '=', True), ('period_id', '=', self.period_id.id), ('payslip_id.state', '=', 'done')])
        employee_stop_ids = [line.payslip_id.employee_id.id for line in employee_stop_lines]
        minus_employee_ids += employee_stop_ids
        result_employee_ids = list((set(employee_ids) - set(minus_employee_ids)))
        res['domain'] = {'employee_id': [('id', 'in', result_employee_ids)]}
        return res

    def get_all_structures_for_payslip(self, cr, uid, structure_id, context):
        structure_ids = [structure_id]
        if not structure_ids:
            return []
        return list(set(self.pool.get('hr.payroll.structure')._get_parent_structure(cr, uid, structure_ids, context=context)))

    def get_days_off_count(self):
        """        
                            احتساب أيام العمل
                    - يتم حذف عدد الأيام في كل سطر  فيه deducted_from_working_days  : ( كف اليد ، طي القيد)
                    - يتم حذف عدد أيام الإجازات : هناك اجازات لا تظهر في المسير  لذلك لا يمكن إستعمال deducted_from_working_days
                     يتم حذف أيام الغياب بدون عذر : من خلال الربط مع الحضور والإنصراف
        """
        res_count = 0.0
        # الإجازات
        # holidays in current periode
        domain = [('employee_id', '=', self.employee_id.id), ('state', 'in', ('done', 'cutoff'))]
        holidays_ids = self.env['hr.holidays'].search(domain)
        for holiday_id in holidays_ids:
            # overlaped days in current month
            holiday_date_from = fields.Date.from_string(holiday_id.date_from)
            date_from = fields.Date.from_string(str(self.date_from))
            holiday_date_to = fields.Date.from_string(str(holiday_id.date_to))
            date_to = fields.Date.from_string(str(self.date_to))
            date_start, date_stop = self.env['hr.smart.utils'].get_overlapped_periode(date_from, date_to, holiday_date_from, holiday_date_to)
            if date_start and date_stop:
                res = self.env['hr.smart.utils'].compute_duration_difference(holiday_id.employee_id, date_start, date_stop, True, True, True)
                if len(res) == 1:
                    rec = res[0]
                    res_count += rec['days']
                else:
                    for rec in res:
                        res_count += rec['days']
        #  غياب‬ بدون ‬عذر
        attendance_summary_ids = self.env['hr.attendance.summary'].search([('employee_id', '=', self.employee_id.id),
                                                                           ('date', '>=', self.date_from),
                                                                           ('date', '<=', self.date_to)
                                                                           ])
        for attendance_summary in attendance_summary_ids:
            res_count += attendance_summary.absence
        # deducted_from_working_days : ( كف اليد ، طي القيد)
        for line in self.line_ids:
            if line.deducted_from_working_days:
                res_count += line.number_of_days
        working_days = 30 - res_count
        if working_days < 0:
            working_days = 0.0
        return working_days

    @api.multi
    def compute_sheet(self):
        bonus_line_obj = self.env['hr.bonus.line']
        loan_obj = self.env['hr.loan']
        for payslip in self:
            # delete old line
            payslip.line_ids.unlink()
            payslip.contraintes_ids.unlink()
            payslip.difference_history_ids.unlink()
            payslip.operation_ids.unlink()
            # change compute_date
            payslip.compute_date = fields.Date.from_string(fields.Date.today())
            # generate  lines
            employee = payslip.employee_id
            # search the salary_grids for this employee
            grid_id, basic_salary = employee.get_salary_grid_id(False)
            if not grid_id:
                continue
            # compute
            lines = []
            sequence = 1
            allowance_total = 0.0
            deduction_total = 0.0
            difference_total = 0.0
            deducted_from_working_days = 0.0
            salary_net_before_deduction = 0.0
            next_periode_id = self.env['hr.period'].search([('id', '>', payslip.period_id.id)], order='id asc', limit=1)
            # --------------
            # 1- الراتب الأساسي
            #  --------------
            basic_salary_val = {'name': u'الراتب الأساسي',
                                'slip_id': payslip.id,
                                'employee_id': employee.id,
                                'rate': 0.0,
                                'number_of_days': 30,
                                'amount': basic_salary,
                                'category': 'basic_salary',
                                'type': 'basic_salary',
                                'sequence': sequence,
                                }
            lines.append(basic_salary_val)
            # --------------
            # 2- البدلات القارة
            # --------------
            res_allowances = employee.get_employee_allowances(grid_id)
            if res_allowances:
                for line in res_allowances:
                    sequence += 1
                    allowance_val = {'name': line['allowance_name'],
                                     'slip_id': payslip.id,
                                     'employee_id': employee.id,
                                     'rate': 0.0,
                                     'number_of_days': 30,
                                     'amount': line['amount'],
                                     'category': 'allowance',
                                     'type': 'allowance',
                                     'sequence': sequence,
                                     }
                    lines.append(allowance_val)
                    allowance_total += line['amount']
            sequence += 1
            # --------------
            # 3- التقاعد‬
            # --------------
            retirement_amount = basic_salary * grid_id.retirement / 100.0
            if retirement_amount:
                retirement_val = {'name': 'التقاعد',
                                  'slip_id': payslip.id,
                                  'employee_id': employee.id,
                                  'rate': 0.0,
                                  'number_of_days': 30,
                                  'amount': retirement_amount * -1,
                                  'category': 'deduction',
                                  'type': 'retirement',
                                  'sequence': sequence}
                lines.append(retirement_val)
                deduction_total += retirement_amount * -1
                sequence += 1
            # --------------
            # 4- المزايا المالية
            # --------------
            bonus_lines = bonus_line_obj.search([('employee_id', '=', employee.id), ('state', '=', 'progress'),
                                                ('period_from_id', '<=', payslip.period_id.id), ('period_to_id', '>=', payslip.period_id.id)])
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
                             'number_of_days': 30,
                             'amount': bonus_amount,
                             'category': 'changing_allowance',
                             'type': bonus_type,
                             'sequence': sequence
                             }
                lines.append(bonus_val)
                allowance_total += bonus_amount
                sequence += 1
            # --------------
            # 4 -  الفروقات
            # --------------
            difference_lines = self.env['hr.differential.line'].search([('difference_id.state', '=', 'done'),
                                                                        ('difference_id.period_id', '=', payslip.period_id.id),
                                                                        ('employee_id', '=', employee.id)])
            for difference in difference_lines:
                sequence += 1
                action_type = difference.difference_id.action_type
                if action_type == 'promotion':
                    difference_name = 'ترقية'
                elif action_type == 'decision_appoint':
                    difference_name = 'تعيين'
                elif action_type == 'tranfert':
                    difference_name = 'نقل'
                elif action_type == 'improve_condition':
                    difference_name = 'تحسين وضع'
                diff_number_of_days = 0.0
                diff_basic_salary_amount = difference.basic_salary_amount
                diff_retirement_amount = difference.retirement_amount
                diff_allowance_amount = difference.allowance_amount
                for rec in difference.defferential_detail_ids:
                    diff_number_of_days += rec.number_of_days
                if diff_basic_salary_amount != 0:
                    difference_val = {'name': 'فرق الراتب الأساسي : '+difference_name,
                                      'slip_id': payslip.id,
                                      'employee_id': employee.id,
                                      'rate': 0.0,
                                      'number_of_days': diff_number_of_days,
                                      'amount': diff_basic_salary_amount,
                                      'category': 'difference',
                                      'type': 'difference',
                                      'sequence': sequence
                                      }
                    lines.append(difference_val)
                    difference_total += diff_basic_salary_amount
                    sequence += 1
                if diff_retirement_amount != 0:
                    difference_val = {'name': 'فرق التقاعد : '+difference_name,
                                      'slip_id': payslip.id,
                                      'employee_id': employee.id,
                                      'rate': 0.0,
                                      'number_of_days': diff_number_of_days,
                                      'amount': diff_retirement_amount,
                                      'category': 'difference',
                                      'type': 'difference',
                                      'sequence': sequence
                                      }
                    lines.append(difference_val)
                    difference_total += diff_retirement_amount
                    sequence += 1
                if diff_allowance_amount != 0:
                    difference_val = {'name': 'فرق البدلات : '+difference_name,
                                      'slip_id': payslip.id,
                                      'employee_id': employee.id,
                                      'rate': 0.0,
                                      'number_of_days': diff_number_of_days,
                                      'amount': diff_allowance_amount,
                                      'category': 'difference',
                                      'type': 'difference',
                                      'sequence': sequence
                                      }
                    lines.append(difference_val)
                    difference_total += diff_allowance_amount
                    sequence += 1
            # --------------
            # 5- الأثر المالي
            # --------------
            difference_lines = payslip.compute_differences()
            for difference in difference_lines:
                sequence += 1
                difference_val = {'name': difference['name'],
                                  'slip_id': payslip.id,
                                  'employee_id': employee.id,
                                  'rate': 0.0,
                                  'number_of_days': difference['number_of_days'],
                                  'amount': difference['amount'],
                                  'category': 'difference',
                                  'type': 'difference',
                                  'deducted_from_working_days': difference.get('deducted_from_working_days', False),
                                  'sequence': sequence,

                                  }
                if difference.get('deducted_from_working_days', False):
                    deducted_from_working_days += difference['number_of_days']
                lines.append(difference_val)
                difference_total += difference['amount']

            #  ، أن كان إذا كان مجموع ما  سيتقاضاه الموظف أقل من ثلث الراتب الأساسي فلا يتم الحسم عليه (حسميات وقروض)
            salary_net_before_deduction += basic_salary - retirement_amount + allowance_total + difference_total
            if salary_net_before_deduction < (basic_salary * 2.0 / 3.0):
                payslip.across_loan = True
            else:
                payslip.across_loan = False
                # --------------
                # 6- الحسميات
                # --------------
                deduction_lines = payslip.compute_deductions(allowance_total)
                for deduction in deduction_lines:
                    deduction_val = {'name': deduction['name'],
                                     'slip_id': payslip.id,
                                     'employee_id': employee.id,
                                     'rate': 0.0,
                                     'number_of_days': deduction['number_of_days'],
                                     'amount': deduction['amount'],
                                     'category': deduction['category'],
                                     'type': deduction['type'],
                                     'sequence': sequence
                                     }
                    lines.append(deduction_val)
                    deduction_total += deduction['amount']
                    sequence += 1
                # --------------
                # 7- القروض
                # --------------
                loans = loan_obj.get_loan_employee_month(payslip.date_from, payslip.date_to, employee.id)
                for loan in loans:
                    loan_val = {'name': loan['name'],
                                'slip_id': payslip.id,
                                'employee_id': employee.id,
                                'rate': 0.0,
                                'number_of_days': 0.0,
                                'amount': loan['amount'] * -1.0,
                                'category': 'deduction',
                                'type': 'loan',
                                'sequence': sequence
                                }
                    lines.append(loan_val)
                    deduction_total += loan['amount'] * -1
                    sequence += 1
            # --------------
            # 8- فرق الحسميات أكثر من ثلث الراتب
            # --------------
            if (deduction_total * -1.0) > basic_salary / 3.0 and not payslip.contraintes_ids:
                third_amount = (deduction_total * -1.0) - basic_salary / 3.0
                vals = {'name': 'فرق الحسميات أكثر من ثلث الراتب',
                        'slip_id': payslip.id,
                        'employee_id': employee.id,
                        'rate': 0.0,
                        'number_of_days': 0.0,
                        'amount': third_amount,
                        'category': 'difference',
                        'type': 'difference',
                        'sequence': sequence
                        }
                lines.append(vals)
                deduction_total += third_amount
                sequence += 1
                if next_periode_id:
                    self.env['hr.payslip.difference.history'].create({'payslip_id': payslip.id,
                                                                      'amount': third_amount,
                                                                      'period_id': next_periode_id.id,
                                                                      'name': 'third_salary'
                                                                      })
                else:
                    raise ValidationError(u".يوجد فروقات متخلدة، يجب إعداد الفترة القادمة")
            # --------------
            # 9- التأمينات‬
            # --------------
            insurance_amount = basic_salary * grid_id.insurance / 100.0
            if insurance_amount:
                insurance_val = {'name': 'التأمين',
                                 'slip_id': payslip.id,
                                 'employee_id': employee.id,
                                 'rate': 0.0,
                                 'number_of_days': 30,
                                 'amount': insurance_amount * -1.0,
                                 'category': 'deduction',
                                 'type': 'insurance',
                                 'sequence': sequence}
                lines.append(insurance_val)
                deduction_total += insurance_amount * -1
                sequence += 1
            diff_line_sequence = sequence
            sequence += 1
            # --------------
            # 10- صافي الراتب
            # --------------
            salary_net = basic_salary + allowance_total + difference_total + deduction_total
            salary_net_val = {'name': u'صافي الراتب',
                              'slip_id': payslip.id,
                              'employee_id': employee.id,
                              'rate': 0.0,
                              'number_of_days': 30,
                              'amount': salary_net,
                              'category': 'salary_net',
                              'type': 'salary_net',
                              'sequence': sequence,
                              }
            lines.append(salary_net_val)
            payslip.salary_net = salary_net
            payslip.line_ids = lines
            # --------------
            # 11- التحقق  إن كان هناك ضوابط يجب التحقق منها
            # --------------
            # - الضابط الوحيد هو إن كان الموظف لديه إجازة ويجب أن لا يقل ما يصرف له عن مبلغ محدد في إعدادات نوع الإجازة
            # get salary_net line
            salary_net_line = self.env['hr.payslip.line'].search([('slip_id', '=', payslip.id), ('type', '=', 'salary_net')])
            for constrainte_line in payslip.contraintes_ids:
                # case 1: check min_amount
                constrainte_name = constrainte_line.constrainte_name
                constrainte_amount = constrainte_line.amount
                if constrainte_name == 'min_amount' and salary_net_line.amount < constrainte_amount:
                    #  ترحيل حسميات الغياب والتأخير إلى الأشهر اللاحقة
                    lines_to_remove = self.env['hr.payslip.line'].search([('slip_id', '=', payslip.id),
                                                                         ('type', 'in', ('retard_leave', 'absence'))])
                    # update calculated net_salary
                    line_amount_deduction = 0.0
                    for line in lines_to_remove:
                        line_amount_deduction += line.amount
                    salary_net_line.amount = salary_net_line.amount - line_amount_deduction
                    # remove deduction line from payslip
                    lines_to_remove.unlink()
                    #  check if net salary is still less than min amount
                    if constrainte_name == 'min_amount' and salary_net_line.amount < constrainte_amount:
                        diff_amount = constrainte_amount - float(salary_net_line.amount)
                        diff_amount_line = self.env['hr.payslip.line'].create({'name': u' فرق الراتب ليصل إلى ' + str(constrainte_amount),
                                                                               'slip_id': payslip.id,
                                                                               'employee_id': employee.id,
                                                                               'rate': 0.0,
                                                                               'number_of_days': 30,
                                                                               'amount': diff_amount,
                                                                               'category': 'difference',
                                                                               'type': 'difference',
                                                                               'sequence': diff_line_sequence,
                                                                               })
                        payslip.line_ids = [(4, diff_amount_line.id)]
                        salary_net_line.amount = salary_net_line.amount + diff_amount
                        # remove delays_ids  and abscence_ids
                        payslip.delays_ids = False
                        payslip.abscence_ids = False
            # case net_salary is negative
            # if salary_net_line.amount < 0:
            #     if next_periode_id:
            #         next_month_amount = salary_net_line.amount
            #         hist_line = self.env['hr.payslip.difference.history'].create({'payslip_id': payslip.id,
            #                                                                       'amount': next_month_amount,
            #                                                                       'period_id': next_periode_id.id,
            #                                                                       'name': 'negative_salary'
            #                                                                       })
            #         if hist_line:
            #             diff_amount_line = self.env['hr.payslip.line'].create({'name': 'المبلغ المرحل (سبب راتب سالب)',
            #                                                                    'slip_id': payslip.id,
            #                                                                    'employee_id': employee.id,
            #                                                                    'rate': 0.0,
            #                                                                    'number_of_days': 30,
            #                                                                    'amount': salary_net_line.amount,
            #                                                                    'category': 'difference',
            #                                                                    'type': 'difference',
            #                                                                    'sequence': diff_line_sequence,
            #                                                                    })
            #             salary_net_line.amount = 0.0
            #     else:
            #         raise ValidationError(u".يوجد فروقات متخلدة، يجب إعداد الفترة القادمة")
            payslip.salary_net = salary_net_line.amount
            # update allowance_total deduction_total
            payslip.allowance_total = allowance_total
            payslip.difference_deduction_total = deduction_total + difference_total
            # calculate work days
            payslip.number_of_days = payslip.get_days_off_count()

    @api.one
    @api.constrains('employee_id', 'period_id')
    def _check_payroll(self):
        for rec in self:
            payroll_count = rec.search_count([('employee_id', '=', rec.employee_id.id),
                                              ('period_id', '=', rec.period_id.id),
                                              ('is_special', '=', False)])
            if payroll_count > 1:
                raise ValidationError(u"لا يمكن إنشاء مسيرين لنفس الموظف في نفس الشهر")

    def get_operations(self, res_model):
        operation_ids = self.operation_ids.search([('payslip_id', '=', self.id), ('res_model', '=', res_model)])
        return [operation.res_id for operation in operation_ids]


class HrPayslipRunError(models.Model):
    _name = 'hr.payslip.run.error'

    payslip_run_id = fields.Many2one('hr.payslip.run', string='المسير', ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string='الموظف')
    type = fields.Selection([('prepaid_holiday', u'إجازة مسبوقة الدفع'),
                             ('stop', u'تم إيقاف راتبه'),
                             ('have_payslip', u'تم إنشاء مسير لهم'),
                             ], required=1, string='السبب')


class HrPayrollConstrainte(models.Model):
    _name = 'hr.payroll.constrainte'

    payslip_id = fields.Many2one('hr.payslip', string=u'الموظف')
    constrainte_name = fields.Selection([('min_amount', u'المبلغ الادنى'),
                                         ], string='الشروط', readonly=1)
    amount = fields.Float(string=u'المبلغ')


class HrPayrollOperation(models.Model):
    _name = 'hr.payroll.operation'

    payslip_id = fields.Many2one('hr.payslip', string='Payslip')
    res_model = fields.Char(string='Model')
    res_id = fields.Integer(string='Model ID')


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
    number_of_days = fields.Float(string='عدد الأيام')
    number_of_hours = fields.Float(string='عدد الساعات')
    deducted_from_working_days = fields.Boolean(string='تخصم  من أيام العمل')
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
                             ('sanction', 'عقوبة'),
                             ('one_third_salary', 'ثلث الراتب'),
                             ], string='النوع', select=1, readonly=1)
    model_name = fields.Char('model name')
    object_id = fields.Integer('Object name')


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

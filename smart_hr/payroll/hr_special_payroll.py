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

    special_state = fields.Selection([('new', 'جديد'),
                                      ('verify', 'المراجعة'),
                                      ('division_director', 'مدير الشعبة'),
                                      ('hrm', 'مدير الشؤون الموظفين'),
                                      ('done', 'منتهية'),
                                      ], 'الحالة', default='new', select=1, readonly=1, copy=False)
    is_special = fields.Boolean(string='مسير خاص')
    speech_number = fields.Char(string=u'رقم الخطاب', readonly=1, states={'draft': [('readonly', 0)]})
    speech_date = fields.Date(string=u'تاريخ الخطاب', readonly=1, states={'draft': [('readonly', 0)]})
    speech_file = fields.Binary(string=u'صورة الخطاب', attachment=True, readonly=1, states={'draft': [('readonly', 0)]})
    payslip_type = fields.Selection([('deputation', 'إنتداب'),
                                     ('overtime', 'خارج الدوام'),
                                     ('transfert', 'نقل'),
                                     ('holidays', 'اجازات مسبوقة الدفع')], 'نوع المسير', select=1, readonly=1, states={'draft': [('readonly', 0)]})
    period_ids = fields.Many2many('hr.period', string=u'الفترات', readonly=1, states={'draft': [('readonly', 0)]})

    @api.multi
    def special_compute_sheet(self):
        self.slip_ids.unlink()
        self.compute_employee_ids(False)
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
                           'type_id': employee.type_id.id,
                           'is_special': self.is_special,
                           'speech_number': self.speech_number,
                           'speech_date': self.speech_date,
                           'speech_file': self.speech_file,
                           'payslip_type': self.payslip_type,
                           'period_ids': [(6, 0, [x.id for x in self.period_ids])]
                           }
            slip_ids.append(payslip_val)
        self.slip_ids = slip_ids
        self.slip_ids.special_compute_sheet()

    @api.multi
    def action_special_new(self):
        self.ensure_one()
        self.state = 'draft'
        self.special_state = 'new'
        for slip in self.slip_ids:
            slip.action_special_new()

    @api.multi
    def action_special_verify(self):
        self.ensure_one()
        for slip in self.slip_ids:
            slip.action_special_verify()
        self.state = 'verify'
        self.special_state = 'verify'

    @api.multi
    def action_special_division_director(self):
        self.ensure_one()
        self.special_state = 'division_director'
        for slip in self.slip_ids:
            slip.action_special_division_director()

    @api.multi
    def action_special_hrm(self):
        self.ensure_one()
        self.special_state = 'hrm'
        for slip in self.slip_ids:
            slip.action_special_hrm()

    @api.multi
    def action_special_done(self):
        self.ensure_one()
        self.state = 'done'
        self.special_state = 'done'
        for slip in self.slip_ids:
            slip.action_special_done()
        self.generate_file()

    @api.multi
    def button_refuse_division_director(self):
        self.ensure_one()
        self.state = 'verify'
        self.special_state = 'verify'
        for slip in self.slip_ids:
            slip.button_refuse_division_director()

    @api.multi
    def button_refuse_verify(self):
        self.ensure_one()
        self.state = 'draft'
        self.special_state = 'new'
        for slip in self.slip_ids:
            slip.button_refuse_verify()


class HrPayslip(models.Model):
    _name = "hr.payslip"
    _inherit = ['hr.payslip', 'mail.thread']
    _order = 'date_from desc,id desc'
    _rec_name = 'name'

    create_date = fields.Datetime(string=u'تاريخ الطلب', default=fields.Datetime.now(), readonly=1)
    owner_employee_id = fields.Many2one('hr.employee', string='صاحب الطلب',
                                        default=lambda self: self.env['hr.employee'].search([('user_id', '=', self._uid)],
                                                                                            limit=1), required=1, readonly=1)
    payslip_type = fields.Selection([('deputation', 'إنتداب'),
                                     ('overtime', 'خارج الدوام'),
                                     ('transfert', 'نقل'),
                                     ('holidays', 'اجازات مسبوقة الدفع')
                                     ], string=u'نوع المسير', select=1, readonly=1, states={'draft': [('readonly', 0)]})
    special_state = fields.Selection([('new', 'جديد'),
                                      ('verify', 'المراجعة'),
                                      ('division_director', 'مدير الشعبة'),
                                      ('hrm', 'مدير الشؤون الموظفين'),
                                      ('done', 'منتهية'),
                                      ], 'الحالة', default='new', select=1, readonly=1, copy=False)
    is_special = fields.Boolean(string='مسير خاص')
    transport_decision_ids = fields.One2many('hr.transport.decision', 'payslip_id')
    overtime_line_ids = fields.One2many('hr.overtime.ligne', 'payslip_id')
    deputation_ids = fields.One2many('hr.deputation', 'payslip_id')
    transfert_ids = fields.One2many('hr.employee.transfert', 'payslip_id')
    holiday_id = fields.Many2one('hr.holidays')
    speech_number = fields.Char(string=u'رقم الخطاب', readonly=1, states={'draft': [('readonly', 0)]})
    speech_date = fields.Date(string=u'تاريخ الخطاب', readonly=1, states={'draft': [('readonly', 0)]})
    speech_file = fields.Binary(string=u'صورة الخطاب', attachment=True, readonly=1, required=1, states={'draft': [('readonly', 0)]})
    speech_file_name = fields.Char(string='speech_file_name')
    period_ids = fields.Many2many('hr.period', string=u'الفترات', readonly=1, states={'draft': [('readonly', 0)]})

    @api.multi
    def action_special_new(self):
        self.ensure_one()
        self.state = 'draft'
        self.special_state = 'new'

    @api.multi
    def action_special_verify(self):
        self.ensure_one()
        self.number = self.env['ir.sequence'].get('seq.hr.payslip')
        self.state = 'verify'
        self.special_state = 'verify'

    @api.multi
    def action_special_division_director(self):
        self.ensure_one()
        self.special_state = 'division_director'

    @api.multi
    def action_special_hrm(self):
        self.ensure_one()
        self.special_state = 'hrm'

    @api.multi
    def action_special_done(self):
        self.ensure_one()
        for rec in self.transport_decision_ids:
            rec.is_paied = True
        for rec in self.overtime_line_ids:
            rec.is_paied = True
        for rec in self.deputation_ids:
            rec.is_paied = True
        for rec in self.transfert_ids:
            rec.is_paied = True
        if self.holiday_id:
            self.holiday_id.advanced_salary_is_paied = True
        self.state = 'done'
        self.special_state = 'done'

    @api.multi
    def button_refuse_division_director(self):
        self.ensure_one()
        self.state = 'verify'
        self.special_state = 'verify'

    @api.multi
    def button_refuse_verify(self):
        self.ensure_one()
        self.state = 'draft'
        self.special_state = 'new'

    @api.multi
    def special_compute_sheet(self):
        for payslip in self:
            # delete old line
            payslip.line_ids.unlink()
            payslip.transport_decision_ids = []
            payslip.overtime_line_ids = []
            payslip.deputation_ids = []
            payslip.transfert_ids = []
            payslip.compute_date = fields.Date.today()
            # generate  lines
            employee = payslip.employee_id
            # search the newest salary_grid for this employee
            salary_grid, basic_salary = employee.get_salary_grid_id(False)
            if not salary_grid:
                continue
            # compute
            lines = []
            line_ids = []
            salary_net = 0.0

            # فروقات اجازات مسبوقة الدفع
            if payslip.payslip_type == 'holidays':
                holidays_line_ids, salary_net_holidays = payslip.get_special_difference_holidays()
                line_ids += holidays_line_ids
                salary_net += salary_net_holidays
            # فروقات خارج الدوام
            if payslip.payslip_type == 'overtime':
                overtime_line_ids, salary_net_overtime = payslip.get_special_difference_overtime()
                line_ids += overtime_line_ids
                salary_net += salary_net_overtime

            # فروقات الأنتداب
            if payslip.payslip_type == 'deputation':
                deputation_line_ids, salary_net_deputation = payslip.get_special_difference_deputation()
                line_ids += deputation_line_ids
                salary_net += salary_net_deputation
            # فروقات النقل
            if payslip.payslip_type == 'tranfert':
                tranfert_line_ids, salary_net_tranfert = payslip.get_special_difference_transfert()
                line_ids += tranfert_line_ids
                salary_net += salary_net_tranfert

            sequence = 1
            for line in line_ids:
                vals = {'name': line['name'],
                        'slip_id': payslip.id,
                        'employee_id': employee.id,
                        'rate': 0.0,
                        'amount': line['amount'],
                        'number_of_days': line['number_of_days'],
                        'number_of_hours': line['number_of_hours'],
                        'category': line.get('category', False) or 'difference',
                        'type': line['type'],
                        'sequence': sequence
                        }
                lines.append(vals)
                sequence += 1
            payslip.line_ids = lines
            payslip.salary_net = salary_net

    @api.multi
    def get_special_difference_overtime(self):
        salary_net = 0.0
        line_ids = []
        overtime_line_obj = self.env['hr.overtime.ligne']
        grid_detail_allowance_obj = self.env['salary.grid.detail.allowance']
        # 1- overtime
        overtime_setting = self.env['hr.overtime.setting'].search([], limit=1)
        overtime_lines = overtime_line_obj.search([('employee_id', '=', self.employee_id.id),
                                                   ('type_compensation', '=', 'amount'),
                                                   ('is_paied', '=', False),
                                                   ('overtime_id.state', '=', 'finish')])
        if overtime_lines:
            self.overtime_line_ids = overtime_lines.ids

        for overtime in overtime_lines:
            employee = overtime.employee_id
            salary_grid, basic_salary = employee.get_salary_grid_id(False)
            #
            date_from = overtime.date_from
            date_to = overtime.date_to
            # get days witouht weekends and Eids
            number_of_days = self.env['hr.smart.utils'].compute_duration_overtime(date_from, date_to, overtime)
            number_of_hours = overtime.heure_number
            # get number of hours
            total_hours = number_of_days * number_of_hours
            amount_hour = basic_salary / 30.0 / 7.0
            rate_hour = overtime_setting.days_normal
            if overtime.type == 'friday_saturday':
                rate_hour = overtime_setting.days_weekend
            elif overtime.type == 'holidays':
                rate_hour = overtime_setting.days_holidays
            amount = amount_hour * rate_hour / 100.0 * total_hours
            overtime_val = {
                            'name': overtime_setting.allowance_overtime_id.name,
                            'employee_id': employee.id,
                            'number_of_days': number_of_days,
                            'number_of_hours': total_hours,
                            'amount': amount,
                            'type': 'overtime'}
            line_ids.append(overtime_val)
            salary_net += amount
            # add allowance transport
            if number_of_days and employee.grade_id not in overtime_setting.grade_ids:
                # search amount transport from salary grid
                transport_allowance_id = self.env.ref('smart_hr.hr_allowance_type_01').id
                transport_allowances = grid_detail_allowance_obj.search([('grid_detail_id', '=', salary_grid.id), ('allowance_id', '=', transport_allowance_id)])
                transport_amount = 0.0
                if transport_allowances:
                    transport_amount = transport_allowances[0].get_value(employee.id) / 30.0 * number_of_days
                allowance_transport_val = {
                                           'name': overtime_setting.allowance_transport_id.name,
                                           'employee_id': employee.id,
                                           'number_of_days': number_of_days,
                                           'number_of_hours': total_hours,
                                           'amount': transport_amount,
                                           'type': 'overtime'}
                line_ids.append(allowance_transport_val)
                salary_net += transport_amount
        return line_ids, salary_net

    @api.multi
    def get_special_difference_deputation(self):
        line_ids = []
        salary_net = 0.0
        deputation_obj = self.env['hr.deputation']
        deputations = deputation_obj.search([('employee_id', '=', self.employee_id.id),
                                             ('is_paied', '=', False),
                                             ('state', '=', 'finish')])
        if deputations:
            self.deputation_ids = deputations.ids
        for deputation in deputations:
            date_from = deputation.date_from
            date_to = deputation.date_to
            number_of_days = self.env['hr.smart.utils'].compute_duration_deputation(date_from, date_to, deputation)
            #
            employee = deputation.employee_id
            # get a correct line
            deputation_amount, transport_amount, deputation_allowance = deputation.get_deputation_allowance_amount(number_of_days)
            if transport_amount:
                # بدل نقل
                transport_val = {
                                 'name': deputation_allowance.allowance_transport_id.name,
                                 'employee_id': employee.id,
                                 'number_of_days': number_of_days,
                                 'number_of_hours': 0.0,
                                 'amount': transport_amount,
                                 'type': 'deputation'}
                line_ids.append(transport_val)
                salary_net += transport_amount
            if deputation_amount:
                deputation_amount_rate = 1.0
                if deputation.the_availability == 'hosing_and_food':
                    deputation_amount_rate = 0.25
                elif deputation.the_availability == 'hosing_or_food':
                    deputation_amount_rate = 0.5
                deputation_amount = deputation_amount * deputation_amount_rate
                # بدل إنتداب
                deputation_val = {
                                  'name': deputation_allowance.allowance_deputation_id.name,
                                  'employee_id': employee.id,
                                  'number_of_days': number_of_days,
                                  'number_of_hours': 0.0,
                                  'amount': deputation_amount,
                                  'type': 'deputation'}
                line_ids.append(deputation_val)
                salary_net += deputation_amount
        # أوامر الإركاب
        transport_decision_ids = self.env['hr.transport.decision'].search([('employee_id', '=', self.employee_id.id),
                                                                           ('state', '=', 'finish'),
                                                                           ('trasport_type', '=', self.env.ref('smart_hr.data_hr_transport_setting2').id),
                                                                           ('is_paied', '=', False),
                                                                           ])
        if transport_decision_ids:
            self.transport_decision_ids = transport_decision_ids.ids
        for transfert_decision in transport_decision_ids:
            vals = {
                    'name': 'فرق أمر اركاب',
                    'employee_id': transfert_decision.employee_id.id,
                    'number_of_days': 0.0,
                    'number_of_hours': 0.0,
                    'amount': transfert_decision.amount,
                    'type': 'transfert_decision'}
            line_ids.append(vals)
            salary_net += transfert_decision.amount
        return line_ids, salary_net

    @api.multi
    def get_special_difference_transfert(self):
        self.ensure_one()
        line_ids = []
        salary_net = 0.0
        hr_setting = self.env['hr.setting'].search([], limit=1)
        if hr_setting:
            transfert_ids = self.env['hr.employee.transfert'].search([('employee_id', '=', self.employee_id.id),
                                                                      ('is_paied', '=', False),
                                                                      ('state', '=', 'done')])
            if transfert_ids:
                self.transfert_ids = transfert_ids.ids
            for transfert in transfert_ids:
                # get تفاصيل سلم الرواتب
                grid_id, basic_salary = transfert.employee_id.get_salary_grid_id(transfert.create_date)
                if grid_id:
                    # 2- بدل إنتداب
                    amount = (hr_setting.deputation_days * (basic_salary / 30))
                    vals = {
                            'name': hr_setting.allowance_deputation.name,
                            'employee_id': transfert.employee_id.id,
                            'number_of_days': hr_setting.deputation_days,
                            'number_of_hours': 0.0,
                            'amount': amount,
                            'type': 'transfert'}
                    line_ids.append(vals)
                    salary_net += amount
                    # 3- بدل ترحيل
                    amount = hr_setting.deportation_amount
                    vals = {
                            'name': hr_setting.allowance_deportation.name,
                            'employee_id': transfert.employee_id.id,
                            'number_of_days': 0,
                            'number_of_hours': 0.0,
                            'amount': amount,
                            'type': 'transfert'}
                    line_ids.append(vals)
                    salary_net += amount
        # أوامر الإركاب
        transport_decision_ids = self.env['hr.transport.decision'].search([('employee_id', '=', self.employee_id.id),
                                                                           ('state', '=', 'finish'),
                                                                           ('trasport_type', '=', self.env.ref('smart_hr.data_hr_transport_setting3').id),
                                                                           ('is_paied', '=', False),
                                                                           ])
        if transport_decision_ids:
            self.transport_decision_ids = transport_decision_ids.ids
        for transfert_decision in transport_decision_ids:
            vals = {
                    'name': 'فرق أمر اركاب',
                    'employee_id': transfert_decision.employee_id.id,
                    'number_of_days': 0.0,
                    'number_of_hours': 0.0,
                    'amount': transfert_decision.amount,
                    'type': 'transfert_decision'}
            line_ids.append(vals)
            salary_net += transfert_decision.amount
        return line_ids, salary_net

    @api.multi
    def get_special_difference_holidays(self):
        self.ensure_one()
        line_ids = []
        salary_net = 0.0
        employee = self.employee_id
        # search the newest salary_grid for this employee
        salary_grid, basic_salary = employee.get_salary_grid_id(False)
        if not salary_grid:
            return
        holidays_id = self.env['hr.holidays'].search([('state', 'in', ('done', 'cutoff')),
                                                      ('employee_id', '=', self.employee_id.id),
                                                      ('with_advanced_salary', '=', True),
                                                      ('advanced_salary_is_paied', '=', False)], limit=1)
        if holidays_id:
            self.holiday_id = holidays_id.id
            salary_multiplication = holidays_id.salary_number
            # --------------
            # 1- الراتب الأساسي
            # --------------
            amount = basic_salary * salary_multiplication
            basic_salary_val = {'name': u'الراتب الأساسي',
                                'employee_id': employee.id,
                                'rate': 0.0,
                                'number_of_days': 30.0 * salary_multiplication,
                                'number_of_hours': 0.0,
                                'amount': amount,
                                'category': 'basic_salary',
                                'type': 'basic_salary',
                                }
            line_ids.append(basic_salary_val)
            salary_net += amount
            # --------------
            # 2- البدلات القارة
            # --------------
            for allowance in employee.get_employee_allowances(salary_grid):
                amount = allowance['amount'] * salary_multiplication
                allowance_val = {'name': allowance['allowance_name'],
                                 'employee_id': employee.id,
                                 'rate': 0.0,
                                 'number_of_days': 30.0 * salary_multiplication,
                                 'number_of_hours': 0.0,
                                 'amount': amount,
                                 'category': 'allowance',
                                 'type': 'allowance',
                                 }
                line_ids.append(allowance_val)
                salary_net += amount
            # --------------
            # 3- التقاعد
            # --------------
            retirement_amount = -1.0 * basic_salary * salary_grid.retirement / 100.0 * salary_multiplication
            if retirement_amount:
                retirement_val = {'name': 'التقاعد',
                                  'employee_id': employee.id,
                                  'rate': 0.0,
                                  'number_of_days': 30.0 * salary_multiplication,
                                  'number_of_hours': 0.0,
                                  'amount': retirement_amount,
                                  'category': 'deduction',
                                  'type': 'retirement'
                                  }
                line_ids.append(retirement_val)
                salary_net += retirement_amount
            # --------------
            # 4- التأمينات
            # --------------
            insurance_amount = -1.0 * basic_salary * salary_grid.insurance / 100.0 * salary_multiplication
            if insurance_amount:
                insurance_val = {'name': 'التأمين',
                                 'employee_id': employee.id,
                                 'rate': 0.0,
                                 'number_of_days': 30.0 * salary_multiplication,
                                 'number_of_hours': 0.0,
                                 'amount': insurance_amount,
                                 'category': 'deduction',
                                 'type': 'insurance'
                                 }
                line_ids.append(insurance_val)
                salary_net += insurance_amount
            # --------------
            # 5- صافي الراتب
            # --------------
            salary_net_val = {'name': u'صافي الراتب',
                              'employee_id': employee.id,
                              'rate': 0.0,
                              'number_of_days': 30.0 * salary_multiplication,
                              'number_of_hours': 0.0,
                              'amount': salary_net,
                              'category': 'salary_net',
                              'type': 'salary_net',
                              }
            line_ids.append(salary_net_val)
        return line_ids, salary_net

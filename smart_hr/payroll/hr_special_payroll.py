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


class HrPayslip(models.Model):
    _name = "hr.payslip"
    _inherit = ['hr.payslip', 'mail.thread']
    _order = 'date_from desc,id desc'
    _rec_name = 'name'

    @api.multi
    def get_default_payslip_type_ids(self):
        return self.env['hr.special.payslip.type'].search([]).ids

    create_date = fields.Datetime(string=u'تاريخ الطلب', default=fields.Datetime.now(), readonly=1)
    owner_employee_id = fields.Many2one('hr.employee', string='صاحب الطلب',
                                        default=lambda self: self.env['hr.employee'].search([('user_id', '=', self._uid)],
                                                                                            limit=1), required=1, readonly=1)
    payslip_type_ids = fields.Many2many('hr.special.payslip.type', string=u'نوع المسير', default=get_default_payslip_type_ids)
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
    speech_number = fields.Char(string=u'رقم الخطاب', readonly=1, states={'draft': [('readonly', 0)]})
    speech_date = fields.Date(string=u'تاريخ الخطاب', readonly=1, states={'draft': [('readonly', 0)]})
    speech_file = fields.Binary(string=u'صورة الخطاب', attachment=True, readonly=1, required=1, states={'draft': [('readonly', 0)]})

    @api.multi
    def action_special_new(self):
        self.ensure_one()
        self.state = 'draft'
        self.special_state = 'new'

    @api.multi
    def action_special_verify(self):
        self.ensure_one()
        self.special_compute_sheet()
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
            # generate  lines
            employee = payslip.employee_id
            # search the newest salary_grid for this employee
            salary_grid, basic_salary = employee.get_salary_grid_id(False)
            if not salary_grid:
                return
            # compute
            lines = []
            line_ids = []
            sequence = 1
            # أوامر الإركاب
            if self.env.ref('smart_hr.hr_special_payslip_type_transport') in self.payslip_type_ids:
                line_ids += self.get_difference_transport_decision()
            # فروقات خارج الدوام
            if self.env.ref('smart_hr.hr_special_payslip_type_overtime') in self.payslip_type_ids:
                line_ids += self.get_difference_overtime()
            # فروقات الأنتداب
            if self.env.ref('smart_hr.hr_special_payslip_type_allowance') in self.payslip_type_ids:
                line_ids += self.get_difference_deputation()
            # فروقات النقل
            if self.env.ref('smart_hr.hr_special_payslip_type_tranfert') in self.payslip_type_ids:
                line_ids += self.get_difference_transfert()

            for line_id in line_ids:
                vals = {'name': line_id['name'],
                        'slip_id': payslip.id,
                        'employee_id': employee.id,
                        'rate': 0.0,
                        'amount': line_id['amount'],
                        'category': 'difference',
                        'type': 'difference',
                        'sequence': sequence
                        }
                lines.append(vals)
                sequence += 1
            payslip.line_ids = lines

    @api.multi
    def get_difference_transport_decision(self):
        self.ensure_one()
        line_ids = []
        transport_decision_ids = self.env['hr.transport.decision'].search([('employee_id', '=', self.employee_id.id),
                                                                           ('state', '=', 'done'),
                                                                           ('is_paied', '=', False),
                                                                           ])
        if transport_decision_ids:
            self.transport_decision_ids = transport_decision_ids.ids
        for transfert_decision in transport_decision_ids:
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
    def get_difference_overtime(self):
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
        # TODO: dont compute not work days
        for overtime in overtime_lines:
            employee = overtime.employee_id
            salary_grid, basic_salary = employee.get_salary_grid_id(False)
            #
            date_from = overtime.date_from
            date_to = overtime.date_to
            # get days witouht weekends and Eids
            number_of_days = self.env['hr.smart.utils'].compute_duration_overtime(date_from, date_to, overtime)
            number_of_hours = 0.0
            if overtime.date_from >= self.date_from and overtime.date_to <= self.date_to:
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
            overtime_val = {'difference_id': self.id,
                            'name': overtime_setting.allowance_overtime_id.name,
                            'employee_id': employee.id,
                            'number_of_days': number_of_days,
                            'number_of_hours': number_of_hours,
                            'amount': amount,
                            'type': 'overtime'}
            line_ids.append(overtime_val)
            # add allowance transport
            if number_of_days and employee.grade_id not in overtime_setting.grade_ids:
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
        return line_ids


class HrSpecialPayslipType(models.Model):
    _name = 'hr.special.payslip.type'
    name = fields.Char(string='نوع المسير')


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
    speech_number = fields.Char(string=u'رقم الخطاب', readonly=1, required=1, states={'draft': [('readonly', 0)]})
    speech_date = fields.Date(string=u'تاريخ الخطاب', readonly=1, required=1, states={'draft': [('readonly', 0)]})
    speech_file = fields.Binary(string=u'صورة الخطاب', attachment=True, readonly=1, required=1, states={'draft': [('readonly', 0)]})

    @api.multi
    def special_compute_sheet(self):
        self.slip_ids.unlink()
        payslip_obj = self.env['hr.payslip']
        for employee in self.employee_ids:
            payslip_val = {'employee_id': employee.id,
                           'month': self.month,
                           'name': _('راتب موظف %s لشهر %s') % (employee.display_name, self.month),
                           'payslip_run_id': self.id,
                           'date_from': self.date_start,
                           'date_to': self.date_end,
                           'is_special': self.is_special,
                           'speech_number': self.speech_number,
                           'speech_date': self.speech_date,
                           'speech_file': self.speech_file,
                           }
            payslip = payslip_obj.create(payslip_val)
            payslip.onchange_employee()
            payslip.special_compute_sheet()

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
        self.special_compute_sheet()
        self.number = self.env['ir.sequence'].get('seq.hr.payslip')
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

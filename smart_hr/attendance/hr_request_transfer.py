# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError
from openerp.addons.smart_base.util.umalqurra import *
from umalqurra.hijri_date import HijriDate
from umalqurra.hijri import Umalqurra


class HrRequestTransferDelayHours(models.Model):
    _name = 'hr.request.transfer.delay.hours'
    _inherit = ['mail.thread']
    _order = 'id desc'
    _description = u'طلبات تحويل ساعات التأخير'

    name = fields.Char(string='التسلسل', readonly=1)
    date = fields.Date(string='تاريخ الطلب', required=1, readonly=1, default=fields.Datetime.now())
    employee_ids = fields.One2many('hr.employee.delay.hours', 'request_id', string='الموظفون', readonly=1,
                                   states={'dm': [('readonly', 0)]})
    description = fields.Text(string=' ملاحظات ')
    state = fields.Selection([('dm', u'مدير المباشر'),
                              ('audit', u'تدقيق'),
                              ('hrm', u'مدير شؤون الموظفين'),
                              ('done', u'اعتماد'),
                              ('refuse', u'رفض'),
                              ], string='الحالة', readonly=1, default='dm')
    department_level1_id = fields.Many2one('hr.department', string='الفرع', readonly=1,
                                           states={'dm': [('readonly', 0)]})
    department_level2_id = fields.Many2one('hr.department', string='القسم', readonly=1,
                                           states={'dm': [('readonly', 0)]})
    department_level3_id = fields.Many2one('hr.department', string='الشعبة', readonly=1,
                                           states={'dm': [('readonly', 0)]})
    salary_grid_type_id = fields.Many2one('salary.grid.type', string='الصنف', readonly=1,
                                          states={'dm': [('readonly', 0)]}, )
    speech_source = fields.Char(string=u'مصدر الخطاب')
    num_speech = fields.Char(string=u'رقم الخطاب الصادر')
    date_speech = fields.Date(string=u'تاريخ الخطاب الصادر')
    speech_file = fields.Binary(string=u'الخطاب الصادر', attachment=True)
    speech_file_name = fields.Char(string=u'file name')
    decission_id = fields.Many2one('hr.decision', string=u'القرارات')

    @api.multi
    def button_request_transfer_delay_hours(self):
        decision_obj = self.env['hr.decision']
        if self.decission_id:
            decission_id = self.decission_id.id
        else:
            decision_type_id = 1
            decision_date = fields.Date.today()  # new date
            if self.num_speech:
                decision_type_id = self.env.ref('smart_hr.data_decision_type__transfer_delay_hours').id
            # create decission
            decission_val = {
                # 'name': self.env['ir.sequence'].get('seq.hr.request.transfer.delay'),
                'decision_type_id': decision_type_id,
                'date': decision_date,
                'employee_id': False}
            decision = decision_obj.create(decission_val)
            decision.text = decision.replace_text(False, decision_date, decision_type_id, 'employee',
                                                  args={'DATE': self.date})
            decission_id = decision.id
            self.decission_id = decission_id
        return {
            'name': _(u'قرار حسم بسبب  التأخير'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.decision',
            'view_id': self.env.ref('smart_hr.hr_decision_wizard_form').id,
            'type': 'ir.actions.act_window',
            'res_id': decission_id,
            'target': 'new'
        }

    @api.multi
    def action_audit(self):
        self.name = self.env['ir.sequence'].get('seq.hr.request.transfer.delay')
        if not self.employee_ids:
            raise ValidationError(u"الرجاء مراجعة الموظفون")
        self.state = 'audit'

    @api.multi
    def action_hrm(self):
        self.state = 'hrm'

    @api.multi
    def action_done(self):
        self.state = 'done'
        for employee in self.employee_ids:
            employee.employee_id.delay_hours_balance -= employee.number_request * 7

    @api.multi
    def button_cancel(self):
        self.state = 'cancel'

    @api.multi
    def button_refuse(self):
        self.state = 'refuse'

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'dm':
                raise ValidationError(u'لا يمكن حذفطلبات تحويل ساعات التأخير فى هذه المرحلة يرجى مراجعة مدير النظام')
        return super(HrRequestTransferDelayHours, self).unlink()


class HrEmployeeDelayHours(models.Model):
    _name = 'hr.employee.delay.hours'
    _inherit = ['mail.thread']
    _order = 'id desc'
    _description = u'  ساعات تأخير الموظفين'

    name = fields.Char(string='التسلسل', readonly=1)
    employee_id = fields.Many2one('hr.employee', string=u'الموظف', domain=[('employee_state', '=', 'employee')],
                                  required=1)
    number_request = fields.Integer(string='عدد الايام المراد تحويلها', required=1)
    balance = fields.Float(string='الرصيد الحالي(ساعات)', readonly=1)
    request_id = fields.Many2one('hr.request.transfer.delay.hours')
    deduction = fields.Boolean(string='is deducted', default=False)

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        dapartment_obj = self.env['hr.department']
        employee_obj = self.env['hr.employee']
        department_level1_id = self.request_id.department_level1_id and self.request_id.department_level1_id.id or False
        department_level2_id = self.request_id.department_level2_id and self.request_id.department_level2_id.id or False
        department_level3_id = self.request_id.department_level3_id and self.request_id.department_level3_id.id or False
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
        if self.request_id.salary_grid_type_id:
            employee_ids = employee_obj.search(
                [('id', 'in', employee_ids), ('type_id', '=', self.request_id.salary_grid_type_id.id)]).ids
        result.update({'domain': {'employee_id': [('id', 'in', employee_ids)]}})
        if self.employee_id:
            self.balance = self.employee_id.delay_hours_balance

        return result

    @api.onchange('number_request')
    def onchange_number_request(self):
        if self.number_request * 7 > self.balance:
            self.number_request = self.balance // 7
            warning = {'title': _('تحذير!'), 'message': _(u'رصيد الموظف غير كافي')}
            return {'warning': warning}


class HrRequestTransferAbsence(models.Model):
    _name = 'hr.request.transfer.absence'
    _inherit = ['mail.thread']
    _order = 'id desc'
    _description = u'طلبات تحويل ايام الغياب بدون عذر'

    name = fields.Char(string='التسلسل', readonly=1)
    date = fields.Date(string='تاريخ الطلب', required=1, readonly=1, default=fields.Datetime.now())
    employee_ids = fields.One2many('hr.employee.absence.days', 'request_id', string='الموظفون', readonly=1,
                                   states={'dm': [('readonly', 0)]})
    description = fields.Text(string=' ملاحظات ')
    state = fields.Selection([('dm', u'مدير المباشر'),
                              ('audit', u'تدقيق'),
                              ('hrm', u'مدير شؤون الموظفين'),
                              ('done', u'اعتماد'),
                              ('refuse', u'رفض'),
                              ], string='الحالة', readonly=1, default='dm')
    speech_source = fields.Char(string=u'مصدر الخطاب')
    num_speech = fields.Char(string=u'رقم الخطاب الصادر')
    date_speech = fields.Date(string=u'تاريخ الخطاب الصادر')
    speech_file = fields.Binary(string=u'الخطاب الصادر', attachment=True)
    decission_id = fields.Many2one('hr.decision', string=u'القرارات')

    @api.multi
    def button_request_transfer_absence(self):
        decision_obj = self.env['hr.decision']
        if self.decission_id:
            decission_id = self.decission_id.id
        else:
            decision_type_id = 1
            decision_date = fields.Date.today()  # new date
            if self.num_speech:
                decision_type_id = self.env.ref('smart_hr.data_decision_type_transfer_absence').id
            # create decission
            decission_val = {
                #   'name': self.env['ir.sequence'].get('seq.hr.request.transfer.delay'),
                'decision_type_id': decision_type_id,
                'date': decision_date,
                'employee_id': False}
            decision = decision_obj.create(decission_val)
            decision.text = decision.replace_text(False, decision_date, decision_type_id, 'employee',
                                                  args={'DATE': self.date})
            decission_id = decision.id
            self.decission_id = decission_id
        return {
            'name': _(u'قرار حسم بسبب الغياب عن العمل'),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.decision',
            'view_id': self.env.ref('smart_hr.hr_decision_wizard_form').id,
            'type': 'ir.actions.act_window',
            'res_id': decission_id,
            'target': 'new'
        }

    @api.multi
    def action_audit(self):
        self.name = self.env['ir.sequence'].get('seq.hr.request.transfer.absence')
        if not self.employee_ids:
            raise ValidationError(u"الرجاء مراجعة الموظفون")
        self.state = 'audit'

    @api.multi
    def action_hrm(self):
        self.state = 'hrm'

    @api.multi
    def action_done(self):
        self.state = 'done'
        for employee in self.employee_ids:
            employee.employee_id.absence_balance -= employee.number_request

    @api.multi
    def button_cancel(self):
        self.state = 'cancel'

    @api.multi
    def button_refuse(self):
        self.state = 'refuse'


class HrEmployeeAbsenceDays(models.Model):
    _name = 'hr.employee.absence.days'
    _inherit = ['mail.thread']
    _order = 'id desc'
    _description = u'   ايام الغياب بدون عذر الموظفين'

    @api.one
    @api.depends('line_ids.deduction')
    def _get_number_request(self):
        self.number_request = len([line.id for line in self.line_ids if line.deduction])

    name = fields.Char(string='التسلسل', readonly=1)
    employee_id = fields.Many2one('hr.employee', string=u'الموظف', domain=[('employee_state', '=', 'employee')],
                                  required=1)
    number_request = fields.Integer(string='عدد الايام التي تم تحويلها', compute="_get_number_request", readonly=1)
    balance = fields.Float(string='الرصيد الحالي(ايام)', readonly=1)
    request_id = fields.Many2one('hr.request.transfer.absence')
    line_ids = fields.One2many('hr.employee.absence.detail', 'absence_days_id', string='أيام الغياب')

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        if self.employee_id:
            self.balance = self.employee_id.absence_balance

    @api.multi
    def action_deduction_all(self):
        for line in self.line_ids:
            line.action_deduction()

    @api.multi
    def action_open_line(self):
        self.ensure_one()
        if not self.line_ids:
            lines = []
            attendances = self.env['hr.attendance.summary'].search([('employee_id', '=', self.employee_id.id), ('deduction', '=', False)])
            for attendance in attendances:
                lines.append({'date': attendance.date, 'attendance_summary_id': attendance.id})
            self.line_ids = lines
        return {
            'name': _(u'ايام الغياب بدون عذر '),
            'view_type': 'form',
            'view_mode': 'form',
            'res_model': 'hr.employee.absence.days',
            'view_id': self.env.ref('smart_hr.hr_employee_absence_days_form').id,
            'type': 'ir.actions.act_window',
            'res_id': self.id,
            'target': 'new',
            'context':  {'readonly_by_pass': True}
            }


class HrEmployeeAbsenceDetail(models.Model):
    _name = 'hr.employee.absence.detail'

    absence_days_id = fields.Many2one('hr.employee.absence.days')
    attendance_summary_id = fields.Many2one('hr.attendance.summary')
    date = fields.Char(string='التاريخ')
    deduction = fields.Boolean(string='حسم')
    is_paied = fields.Boolean(string='تم الحسم في الرواتب')

    @api.multi
    def action_deduction(self):
        for rec in self:
            rec.deduction = True
            rec.attendance_summary_id.deduction = True

    @api.multi
    def action_cancel_deduction(self):
        for rec in self:
            rec.deduction = False
            rec.attendance_summary_id.deduction = False

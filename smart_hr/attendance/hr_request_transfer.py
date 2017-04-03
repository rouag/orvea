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
    employee_ids = fields.One2many('hr.employee.delay.hours', 'request_id', string='الموظفون', readonly=1, states={'dm': [('readonly', 0)]})
    description = fields.Text(string=' ملاحظات ')
    state = fields.Selection([('dm', u'مدير المباشر'),
                              ('audit', u'تدقيق'),
                              ('hrm', u'مدير شؤون الموظفين'),
                              ('done', u'اعتماد'),
                              ('refuse', u'رفض'),
                              ], string='الحالة', readonly=1, default='dm')
    department_level1_id = fields.Many2one('hr.department', string='الفرع', readonly=1, states={'dm': [('readonly', 0)]})
    department_level2_id = fields.Many2one('hr.department', string='القسم', readonly=1, states={'dm': [('readonly', 0)]})
    department_level3_id = fields.Many2one('hr.department', string='الشعبة', readonly=1, states={'dm': [('readonly', 0)]})
    salary_grid_type_id = fields.Many2one('salary.grid.type', string='الصنف', readonly=1, states={'dm': [('readonly', 0)]},)

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
            employee.employee_id.delay_hours_balance -= employee.number_request

    @api.multi
    def button_cancel(self):
        self.state = 'cancel'

    @api.multi
    def button_refuse(self):
        self.state = 'refuse'


class HrEmployeeDelayHours(models.Model):

    _name = 'hr.employee.delay.hours'
    _inherit = ['mail.thread']
    _order = 'id desc'
    _description = u'  ساعات تأخير الموظفين'

    name = fields.Char(string='التسلسل', readonly=1)
    employee_id = fields.Many2one('hr.employee', string=u'الموظف', domain=[('employee_state', '=', 'employee')], resquired=1)
    number_request = fields.Integer(string='عدد الساعات المراد تحويلها', required=1)
    balance = fields.Float(string='الرصيد الحالي', readonly=1, related='employee_id.delay_hours_balance')
    request_id = fields.Many2one('hr.request.transfer.delay.hours')

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
            employee_ids = employee_obj.search([('id', 'in', employee_ids), ('type_id', '=', self.request_id.salary_grid_type_id.id)]).ids
        result.update({'domain': {'employee_id': [('id', 'in', employee_ids)]}})
        return result

    @api.onchange('number_request')
    def onchange_number_request(self):
        if self.number_request > self.balance:
            self.number_request = 0.0
            warning = {'title': _('تحذير!'), 'message': _(u'رصيد الموظف غير كافي')}
            return {'warning': warning}



class HrRequestTransferAbsence(models.Model):
    _name = 'hr.request.transfer.absence'
    _inherit = ['mail.thread']
    _order = 'id desc'
    _description = u'طلبات تحويل ايام الغياب بدون عذر'

    name = fields.Char(string='التسلسل', readonly=1)
    date = fields.Date(string='تاريخ الطلب', required=1, readonly=1, default=fields.Datetime.now())
    employee_ids = fields.One2many('hr.employee.absence.days', 'request_id', string='الموظفون', readonly=1, states={'dm': [('readonly', 0)]})
    description = fields.Text(string=' ملاحظات ')
    state = fields.Selection([('dm', u'مدير المباشر'),
                              ('audit', u'تدقيق'),
                              ('hrm', u'مدير شؤون الموظفين'),
                              ('done', u'اعتماد'),
                              ('refuse', u'رفض'),
                              ], string='الحالة', readonly=1, default='dm')
    department_level1_id = fields.Many2one('hr.department', string='الفرع', readonly=1, states={'dm': [('readonly', 0)]})
    department_level2_id = fields.Many2one('hr.department', string='القسم', readonly=1, states={'dm': [('readonly', 0)]})
    department_level3_id = fields.Many2one('hr.department', string='الشعبة', readonly=1, states={'dm': [('readonly', 0)]})
    salary_grid_type_id = fields.Many2one('salary.grid.type', string='الصنف', readonly=1, states={'dm': [('readonly', 0)]},)
    employee_id_domain = fields.Char()

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

    name = fields.Char(string='التسلسل', readonly=1)
    employee_id = fields.Many2one('hr.employee', string=u'الموظف', domain=[('employee_state', '=', 'employee')], resquired=1)
    number_request = fields.Integer(string='عدد الايام المراد تحويلها', required=1)
    balance = fields.Float(string='الرصيد الحالي', readonly=1, related='employee_id.absence_balance')
    request_id = fields.Many2one('hr.request.transfer.absence')

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
            employee_ids = employee_obj.search([('id', 'in', employee_ids), ('type_id', '=', self.request_id.salary_grid_type_id.id)]).ids
        result.update({'domain': {'employee_id': [('id', 'in', employee_ids)]}})
        return result

    @api.onchange('number_request')
    def onchange_number_request(self):
        if self.number_request > self.balance:
            self.number_request = 0.0
            warning = {'title': _('تحذير!'), 'message': _(u'رصيد الموظف غير كافي')}
            return {'warning': warning}


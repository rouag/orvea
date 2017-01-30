# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import ValidationError


class HrRequestTransfer(models.Model):
    _name = 'hr.request.transfer'
    _inherit = ['mail.thread']
    _order = 'id desc'
    _description = u'طلبات تحويل ساعات التأخير'

    name = fields.Char(string='التسلسل', readonly=1)
    employee_id = fields.Many2one('hr.employee', string='الموظف', required=1, domain=[('employee_state', '=', 'employee')],
                                  readonly=1, states={'new': [('readonly', 0)]})
    number = fields.Char(string='الرقم الوظيفي', readonly=1)
    department_id = fields.Many2one('hr.department', string='الادارة', readonly=1)
    job_id = fields.Many2one('hr.job', string='الوظيفة', readonly=1)
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة', readonly=1)
    description = fields.Text(string=' ملاحظات ')
    state = fields.Selection([('new', 'طلب'),
                              ('waiting', 'في إنتظار الإعتماد'),
                              ('cancel', 'مرفوض'),
                              ('done', 'اعتمدت')], string='الحالة', readonly=1, default='new')
    date = fields.Date(string='تاريخ الطلب', required=1, readonly=1, states={'new': [('readonly', 0)]}, default=fields.Datetime.now())
    number_request = fields.Float(string='عدد الساعات المراد تحويلها', required=1, readonly=1, states={'new': [('readonly', 0)]})
    balance = fields.Float(string='الرصيد الحالي', readonly=1)

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        if self.employee_id:
            self.number = self.employee_id.number
            self.department_id = self.employee_id.job_id.department_id
            self.job_id = self.employee_id.job_id
            self.grade_id = self.employee_id.job_id.grade_id
            # TODO: compute balance
            self.balance = 2.0

    @api.onchange('number_request', 'type')
    def onchange_number_request(self):
        if self.number_request > self.balance:
            self.number_request = 0.0
            warning = {'title': _('تحذير!'), 'message': _(u'رصيدك غير كافي')}
            return {'warning': warning}

    @api.one
    def action_waiting(self):
        self.name = self.env['ir.sequence'].get('seq.hr.request.transfer')
        self.state = 'waiting'

    @api.multi
    def action_done(self):
        self.state = 'done'

    @api.one
    def action_refuse(self):
        self.state = 'cancel'

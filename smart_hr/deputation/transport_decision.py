# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import Warning
from openerp.exceptions import ValidationError
from openerp.exceptions import UserError
from datetime import date, datetime, timedelta

class HrTransportDecision(models.Model):
    _name = 'hr.transport.decision'
    _order = 'id desc'
    _description = u'أوامر الإركاب'

    order_date = fields.Date(string='تاريخ الطلب', default=fields.Datetime.now(), readonly=1)
    employee_id = fields.Many2one('hr.employee', string=' إسم الموظف', required=1)
    number = fields.Char(string='الرقم الوظيفي', readonly=1)
    code = fields.Char(string=u'رمز الوظيفة ', readonly=1)
    job_id = fields.Many2one('hr.job', string='الوظيفة', store=True, readonly=1)
    number_job = fields.Char(string='رقم الوظيفة', store=True, readonly=1)
    type_id = fields.Many2one('salary.grid.type', string='الصنف', store=True, readonly=1)
    department_id = fields.Many2one('hr.department', string='الادارة', store=True, readonly=1)
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة', store=True, readonly=1)
    degree_id = fields.Many2one('salary.grid.degree', string='الدرجة', store=True, readonly=1)
    note = fields.Text(string=u'الملاحظات', readonly=1, states={'draft': [('readonly', 0)]})
    date_decision = fields.Date(string='تاريخ قرار ')
    file_decision = fields.Binary(string='صورة قرار ')
    airline = fields.Char(string='الخطوط الجوية أو مكتب السفريات')
    state = fields.Selection([
                              ('draft', u'طلب'),
                              ('audit', u'دراسة طلب'),
                              ('done', u'اعتمدت'),
                              ('refuse', u'مرفوض'),
                              ('finish', u'منتهية'),
                              ('cancel', u'ملغى')
                              ], string=u'حالة', default='draft', advanced_search=True)

    @api.multi
    def action_audit(self):
        for deputation in self:
            deputation.state = 'audit'

    @api.multi
    def action_done(self):
        for deputation in self:
            deputation.state = 'done'

    @api.multi
    def action_refuse(self):
        for deputation in self:
            deputation.state = 'refuse'

    @api.multi
    def action_finish(self):
        for deputation in self:
            deputation.state = 'finish'

    @api.multi
    def action_cancel(self):
        for deputation in self:
            deputation.state = 'cancel'

    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id:
            self.number = self.employee_id.number
            appoint_line = self.env['hr.decision.appoint'].search([('employee_id', '=', self.employee_id.id), ('state', '=', 'done')], limit=1)
            if appoint_line:
                self.job_id = appoint_line.job_id.id
                self.code = appoint_line.job_id.name.number
                self.number_job = appoint_line.number
                self.type_id = appoint_line.type_id.id
                self.grade_id = appoint_line.grade_id.id
                self.department_id = appoint_line.department_id.id
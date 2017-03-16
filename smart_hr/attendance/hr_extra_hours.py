# -*- coding: utf-8 -*-

from openerp import models, fields, api, _


class HrExtraHours(models.Model):
    _name = 'hr.extra_hours'
    _inherit = ['mail.thread']
    _order = 'id desc'
    _description = u'الساعات الإضافية'

    name = fields.Char(string='التسلسل', readonly=1)
    employee_id = fields.Many2one('hr.employee', string='الموظف', required=1, domain=[('employee_state', '=', 'employee')],
                                  readonly=1, states={'new': [('readonly', 0)]})
    number = fields.Char(string='رقم الوظيفة', readonly=1)
    department_id = fields.Many2one('hr.department', string='الادارة', readonly=1)
    job_id = fields.Many2one('hr.job', string='الوظيفة', readonly=1)
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة', readonly=1)
    description = fields.Text(string=' ملاحظات ')
    state = fields.Selection([('new', 'طلب'),
                              ('waiting', 'في إنتظار الإعتماد'),
                              ('cancel', 'مرفوض'),
                              ('done', 'اعتمدت')], string='الحالة', readonly=1, default='new')

    date = fields.Date(string='تاريخ الطلب', required=1, readonly=1, states={'new': [('readonly', 0)]})
    hour_from = fields.Float(string='من الساعة', required=1, readonly=1, states={'new': [('readonly', 0)]})
    hour_to = fields.Float(string='إلى', required=1, readonly=1, states={'new': [('readonly', 0)]})
    hour_number = fields.Float(string='عدد الساعات', required=1, readonly=1, states={'new': [('readonly', 0)]})

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        if self.employee_id:
            self.number = self.employee_id.number
            self.department_id = self.employee_id.job_id.department_id
            self.job_id = self.employee_id.job_id
            self.grade_id = self.employee_id.job_id.grade_id

    @api.one
    def action_waiting(self):
        self.name = self.env['ir.sequence'].get('seq.hr.extra_hours')
        self.state = 'waiting'

    @api.multi
    def action_done(self):
        self.state = 'done'

    @api.one
    def button_refuse(self):
        self.state = 'cancel'

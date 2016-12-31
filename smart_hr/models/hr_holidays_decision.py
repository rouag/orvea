# -*- coding: utf-8 -*-

from openerp import models, api, fields, _
from openerp.exceptions import ValidationError


class hrHolidaysDecision(models.Model):
    _name = 'hr.holidays.decision'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string=' إسم الموظف', required=1)
    number = fields.Char(related='employee_id.number', store=True, readonly=True, string=' الرقم الوظيفي')
    job_id = fields.Many2one(related='employee_id.job_id', store=True, readonly=True, string=' الوظيفة')
    department_id = fields.Many2one(related='employee_id.department_id', store=True, readonly=True, string=' القسم')
  #  degree_id = fields.Many2one(related='employee_id.degree_id', store=True, readonly=True, string=' الدرجة')
    date = fields.Date(string=u'تاريخ المباشرة', default=fields.Datetime.now())
    state = fields.Selection([('new', ' ارسال طلب'),
                             ('waiting', 'في إنتظار الإعتماد'),
                             ('cancel', 'رفض'),
                             ('done', 'اعتمدت')], string='الحالة', readonly=1, default='new')

   

    @api.one
    def action_waiting(self):
        self.state = 'waiting'

    @api.one
    def action_cancel(self):
        self.state = 'cancel'

    @api.one
    def action_done(self):
        self.state = 'done'

    @api.one
    def action_refuse(self):
        self.state = 'new'
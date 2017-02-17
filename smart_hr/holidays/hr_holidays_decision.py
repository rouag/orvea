# -*- coding: utf-8 -*-

from openerp import models, api, fields, _
from openerp.exceptions import ValidationError


class hrHolidaysDecision(models.Model):
    _name = 'hr.holidays.decision'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string=' إسم الموظف', required=1)
    number = fields.Char(related='employee_id.number', store=True, readonly=True, string=' الرقم الوظيفي')
    job_id = fields.Many2one(related='employee_id.job_id', store=True, readonly=True, string=' الوظيفة')
    department_id = fields.Many2one(related='employee_id.department_id', store=True, readonly=True, string=' الادارة')
  #  degree_id = fields.Many2one(related='employee_id.degree_id', store=True, readonly=True, string=' الدرجة')
    date = fields.Date(string=u'تاريخ المباشرة', default=fields.Datetime.now(),required=1)
    state = fields.Selection([('new', ' ارسال طلب'),
                             ('waiting', 'في إنتظار الإعتماد'),
                             ('done', 'اعتمدت'),
                             ('cancel', 'رفض')
                             ], string='الحالة', readonly=1, default='new')

    holidays = fields.Many2many('hr.holidays', string=u'الإجازات',required=1)
    name = fields.Char(string='رقم الخطاب', required=1)
    order_date = fields.Date(string='تاريخ الخطاب', required=1) 
    file_decision = fields.Binary(string='الخطاب')
    file_decision_name = fields.Char(string='اسم الخطاب')


    @api.one
    def action_waiting(self):
        self.state = 'waiting'

    @api.one
    def action_cancel(self):
        self.state = 'cancel'

    @api.one
    def action_done(self):
        for holiday in self.holidays:
            type = " مباشرة بعد"+" " +holiday.holiday_status_id.name.encode('utf-8')
            self.env['hr.employee.history'].sudo().add_action_line(self.employee_id, self.name, self.date, type)
        self.state = 'done'

    @api.one
    def action_refuse(self):
        self.state = 'new'

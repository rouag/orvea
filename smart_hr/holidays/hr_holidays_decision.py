# -*- coding: utf-8 -*-

from openerp import models, api, fields, _
from openerp.exceptions import ValidationError


class hrHolidaysDecision(models.Model):
    _name = 'hr.holidays.decision'
    _inherit = ['mail.thread']
    _rec_name = 'employee_id'
    

    employee_id = fields.Many2one('hr.employee', string=' إسم الموظف', required=1)
    number = fields.Char(related='employee_id.number', store=True, readonly=True, string=' رقم الوظيفة')
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
    file_decision = fields.Binary(string='الخطاب', attachment=True)
    file_decision_name = fields.Char(string='اسم الخطاب')

    @api.onchange('date')
    @api.constrains('date')
    def _onchange_date(self):
        if self.date:
            is_holiday = self.env['hr.smart.utils'].check_holiday_weekend_days(self.date, self.employee_id)
            if is_holiday:
                if is_holiday == "official holiday":
                    raise ValidationError(u"هناك تداخل فى تاريخ المباشرة مع اعياد و عطل رسمية")
                elif is_holiday == "weekend":
                    raise ValidationError(u"هناك تداخل فى تاريخ المباشرة مع عطلة نهاية الاسبوع")
                elif is_holiday == "holiday":
                    raise ValidationError(u"هناك تداخل فى تاريخ المباشرة مع يوم إجازة")

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        if self.date and self.employee_id:
            if self.env['hr.holidays'].search_count([('state', '=', 'done'), ('date_from', '<=', self.date), ('date_to', '>=', self.date), ('employee_id', '=', self.employee_id.id)]) != 0:
                raise ValidationError(u"هناك تداخل فى تاريخ المباشرة مع يوم إجازة")

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
    def button_refuse(self):
        self.state = 'new'

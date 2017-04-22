# -*- coding: utf-8 -*-

from openerp import models, api, fields, _
from openerp.exceptions import ValidationError


class hrHolidaysDecision(models.Model):
    _name = 'hr.holidays.decision'
    _inherit = ['mail.thread']
    _rec_name = 'employee_id'


    employee_id = fields.Many2one('hr.employee', string=' إسم الموظف', required=1)
    number = fields.Char(readonly=True, string=' الرقم الوظيفي')
    job_id = fields.Many2one('hr.job', readonly=True, string=' الوظيفة')
    department_id = fields.Many2one('hr.department', readonly=True, string=' الادارة')
  #  degree_id = fields.Many2one(related='employee_id.degree_id', store=True, readonly=True, string=' الدرجة')
    date = fields.Date(string=u'تاريخ المباشرة', default=fields.Datetime.now(),required=1)
    state = fields.Selection([('new', ' ارسال طلب'),
                             ('waiting', 'في إنتظار الإعتماد'),
                             ('done', 'اعتمدت'),
                             ('cancel', 'رفض')
                             ], string='الحالة', readonly=1, default='new')

    holiday_id = fields.Many2one('hr.holidays', string=u'الإجازة',required=1)
    holiday_status_id = fields.Many2one('hr.holidays.status', string=u'نوع الأجازة',readonly=1)
    date_from = fields.Date(string=u'تاريخ البدء ', readonly=True)
    date_to = fields.Date(string=u'تاريخ الإنتهاء', readonly=True)
    duration = fields.Integer(string=u'مدتها' , readonly=True)
    name = fields.Char(string='رقم الخطاب', required=1)
    order_date = fields.Date(string='تاريخ الخطاب', required=1) 
    file_decision = fields.Binary(string='الخطاب', attachment=True)
    file_decision_name = fields.Char(string='اسم الخطاب')

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'new' :
                raise ValidationError(u'لا يمكن حذف قرار المباشرة فى هذه المرحلة يرجى مراجعة مدير النظام')
        return super(hrHolidaysDecision, self).unlink()


    @api.onchange('date')
    @api.constrains('date')
    def _onchange_date(self):
        res = {}
        warning = {}
        self.holiday_status_id = False
        self.date_from = False
        self.date_to = False
        self.duration = 0
        if self.employee_id and self.date :
            holidays = self.env['hr.holidays'].search([('state', '=', 'done'), ('holiday_status_id.direct_decision', '=', True), ('date_to', '<=', self.date), ('employee_id', '=', self.employee_id.id)])
            holidays_ids = []
            if holidays:
                holidays_ids = holidays.ids
                direct_decision_ids = self.search([('holiday_id', 'in', holidays.ids)])
                for direct_decision_id in direct_decision_ids:
                    holidays_ids.remove(direct_decision_id.holiday_id.id)
                res['domain'] = {'holiday_id': [('id', 'in', holidays_ids)]}
        else:
            res['domain'] = {'holiday_id': [('id', 'in', [])]}
        if self.date:
            is_holiday = self.env['hr.smart.utils'].check_holiday_weekend_days(self.date, self.employee_id)
            if is_holiday:
                if is_holiday == "official holiday":
                    warning = {
                        'title': _('تحذير!'),
                        'message': _('هناك تداخل فى تاريخ المباشرة مع اعياد و عطل رسمية!'),
                }
                elif is_holiday == "weekend":
                    warning = {
                        'title': _('تحذير!'),
                        'message': _('هناك تداخل فى تاريخ المباشرة مع عطلة نهاية الاسبوع!'),
                }
                elif is_holiday == "holiday":
                    warning = {
                        'title': _('تحذير!'),
                        'message': _('هناك تداخل فى تاريخ المباشرة مع يوم إجازة!'),
                        }
            res['warning'] = warning
        return res

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        res = {}
        if self.employee_id:
            self.number = self.employee_id.number
            self.job_id = self.employee_id.job_id.id
            self.department_id = self.employee_id.department_id.id
        self.holiday_id = False
        self.holiday_status_id = False
        self.date_from = False
        self.date_to = False
        self.duration = 0
        if self.employee_id and self.date :
            holidays = self.env['hr.holidays'].search([('state', '=', 'done'), ('holiday_status_id.direct_decision', '=', True), ('date_to', '<=', self.date), ('employee_id', '=', self.employee_id.id)])
            holidays_ids = []
            if holidays:
                holidays_ids = holidays.ids
                direct_decision_ids = self.search([('holiday_id', 'in', holidays.ids)])
                for direct_decision_id in direct_decision_ids:
                    holidays_ids.remove(direct_decision_id.holiday_id.id)
                res['domain'] = {'holiday_id': [('id', 'in', holidays.ids)]}
            else:
                res['domain'] = {'holiday_id': [('id', 'in', [])]}
        else:
            res['domain'] = {'holiday_id': [('id', 'in', [])]}
        return res

    @api.onchange('holiday_id')
    def onchange_holiday_id(self):
        res = {}
        if self.holiday_id:
            self.holiday_status_id = self.holiday_id.holiday_status_id.id
            self.date_from = self.holiday_id.date_from
            self.date_to = self.holiday_id.date_to
            self.duration = self.holiday_id.duration

    @api.one
    def action_waiting(self):
        if not self.holiday_id:
            raise ValidationError(u"لا يوجد إجازة للموظف")
        else:
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

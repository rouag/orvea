# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from datetime import date, datetime, timedelta
from openerp.exceptions import ValidationError
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class HrAuthorization(models.Model):
    _name = 'hr.authorization'
    _inherit = ['mail.thread']
    _order = 'id desc'
    _description = u'طلبات الإستئذان'

    name = fields.Char(string='التسلسل', readonly=1)
    employee_id = fields.Many2one('hr.employee', string='الموظف', required=1, domain=[('employee_state', '=', 'employee')],
                                  readonly=1,
                                  default=lambda self: self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1))
    number = fields.Char(string='رقم الوظيفة', readonly=1)
    department_id = fields.Many2one('hr.department', string='الادارة', readonly=1)
    job_id = fields.Many2one('hr.job', string='الوظيفة', readonly=1)
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة', readonly=1)
    type_id = fields.Many2one('hr.authorization.type', string='النوع', required=1, readonly=1, states={'new': [('readonly', 0)]})
    description = fields.Text(string=' ملاحظات ')
    state = fields.Selection([('new', 'طلب'),
                              ('waiting', 'في إنتظار الإعتماد'),
                              ('cancel', 'مرفوض'),
                              ('done', 'اعتمدت')], string='الحالة', readonly=1, default='new')
    date = fields.Date(string='تاريخ الطلب', readonly=1, default=fields.Datetime.now())
    hour_from = fields.Float(string='من الساعة', required=1, readonly=1, states={'new': [('readonly', 0)]})
    hour_to = fields.Float(string='إلى', required=1, readonly=1, states={'new': [('readonly', 0)]})
    hour_number = fields.Float(string='عدد الساعات', required=1, readonly=1)
    current_autorization_stock = fields.Float(string=u'الرصيد الحالي', compute='_compute_current_autorization_stock')
    authorisation_ids = fields.One2many('hr.employee.authorization.history', 'autorisation_id', string=u'سجل الاستئذانات‬ ‫الشهرية‬', readonly=1)

    @api.one
    @api.constrains('hour_from', 'hour_to')
    def check_hours(self):

        if self.hour_from > self.hour_to:
            raise ValidationError(u"الساعة من يجب ان تكون أصغر من الساعة الى")

    @api.onchange('employee_id')
    def onchange_employee_id(self):
        if self.employee_id:
            self.number = self.employee_id.number
            self.department_id = self.employee_id.job_id.department_id
            self.job_id = self.employee_id.job_id
            self.grade_id = self.employee_id.job_id.grade_id

    @api.onchange('hour_from', 'hour_to')
    def onchange_hour(self):
        self.hour_number = self.hour_to - self.hour_from

    @api.one
    def action_waiting(self):
        self.name = self.env['ir.sequence'].get('seq.hr.authorization')
        self.env['base.notification'].create({'title': u'إشعار بوجود طلب إستئذان',
                                              'message': u"لقد تم تقديم  طلب إستئذان من طرف الموظف"+unicode(self.employee_id.user_id.id),
                                              'user_id': self.employee_id.parent_id.user_id.id,
                                              'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                              'notif': True,
                                              'res_id': self.id,
                                             'res_action': 'smart_hr.action_hr_authorization_form'})
        self.state = 'waiting'

    @api.multi
    def action_done(self):
        self.state = 'done'
        authorization_history_obj = self.env['hr.employee.authorization.history']
        authorization_history_obj.create({'employee_id': self.employee_id.id, 'date': self.date, 'hour_number': self.hour_number, 'autorisation_id': self.id})
        self.env['base.notification'].create({'title': u'إشعار بقبول إستئذان',
                                              'message': u'لقد تم قبول الإستئذان',
                                              'user_id': self.employee_id.user_id.id,
                                              'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                              'notif': True,
                                              'res_id': self.id,
                                             'res_action': 'smart_hr.action_hr_authorization_form'})
        
    @api.one
    def button_refuse(self):
        self.state = 'cancel'
        self.env['base.notification'].create({'title': u'إشعار برفض إستئذان',
                                              'message': u'لقد تم رفض الإستئذان',
                                              'user_id': self.employee_id.user_id.id,
                                              'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                              'notif': True,
                                              'res_id': self.id,
                                             'res_action': 'smart_hr.action_hr_authorization_form'})

    @api.multi
    @api.depends('employee_id')
    def _compute_current_autorization_stock(self):
        self.ensure_one()
        authorization_stock_setting_obj = self.env['hr.authorization.stock.setting']
        max_stock = authorization_stock_setting_obj.search([], limit=1).hours_stock
        authorization_history_obj = self.env['hr.employee.authorization.history']
        taken_auth_current_month = authorization_history_obj.search([('employee_id', '=', self.employee_id.id),
                                                                     ('date', '<=', datetime.now()),
                                                                     ('date', '>=', datetime.now().replace(day=1))])
        if taken_auth_current_month:
            current_stock = 0
            for auth in taken_auth_current_month:
                current_stock += auth.hour_number
            self.current_autorization_stock = max_stock - current_stock
        else:
            self.current_autorization_stock = max_stock

    @api.one
    @api.constrains('hour_number')
    def check_hours_stock(self):
        if self.hour_number > self.current_autorization_stock:
            raise ValidationError(u"ليس لديك الرصيد الكافي")


class HrAuthorizationType(models.Model):
    _name = 'hr.authorization.type'
    _description = u'أنواع طلبات الإستئذان'

    name = fields.Char(string='المسمى', required=1)
    code = fields.Char(string='الرمز')
    note = fields.Text(string='ملاحظات')
    sequence = fields.Integer(string='الترتيب')

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = '[%s] %s' % (record.code, record.name)
            result.append((record.id, name))
        return result


class HrAuthorizationStockSetting(models.Model):
    _name = 'hr.authorization.stock.setting'
    _description = u'اعداد رصيد الاستئذان‬ات'
    
    name = fields.Char(string='name', default=u'اعداد رصيد الاستئذان‬ات')
    hours_stock = fields.Float(string='عدد‬ ساعات‬ الاستئذان‬ المسموح‬ بها‬ شهريا')

    @api.multi
    def button_setting(self):
        auth_stock_setting = self.env['hr.authorization.stock.setting'].search([], limit=1)
        if auth_stock_setting:
            value = {
                'name': u'رصيد الاستئذان‬ات',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'hr.authorization.stock.setting',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'res_id': auth_stock_setting.id,
            }
            return value


class HrEmployeeAuthorizationHistory(models.Model):
    _name = 'hr.employee.authorization.history'
    _description = u'سجل الاستئذان‬ات'

    employee_id = fields.Many2one('hr.employee', string='الموظف')
    date = fields.Date(string='تاريخ الطلب')
    hour_number = fields.Float(string='عدد الساعات')
    autorisation_id = fields.Many2one('hr.authorization')

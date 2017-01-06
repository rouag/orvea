# -*- coding: utf-8 -*-

from openerp import fields, models, api, _
from openerp.exceptions import ValidationError
from openerp.tools import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from datetime import date, datetime, timedelta

class HrHolidaysExtension(models.Model):
    _name = 'hr.holidays.extension'
    _description = 'Holidays Extension'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'id desc'

    name = fields.Char(string=u'رقم القرار', advanced_search=True)
    date = fields.Date(string=u'تاريخ الطلب', default=fields.Datetime.now())
    employee_id = fields.Many2one('hr.employee',  string=u'الموظف', domain=[('employee_state','=','employee')], advanced_search=True)
    is_the_creator = fields.Boolean(string='Is Current User', compute='_employee_is_the_creator')
    entitlement_id = fields.Many2one('hr.holidays.status.entitlement', string=u'نوع الاستحقاق')
    holiday_status_id = fields.Many2one('hr.holidays.status','نوع الاجازة', domain="[('entitlements.extension_period', '!=', '0')]")
    state = fields.Selection([
        ('draft', u'طلب'),
        ('audit', u'مراجعة'),
        ('done', u'إعتمد'),
        ('refuse', u'رفض'),
    ], string=u'حالة', default='draft', advanced_search=True)
    note = fields.Text(string = u'الملاحظات', required = True)
    duration = fields.Integer(string=u'الأيام')
    @api.depends('employee_id')
    def _employee_is_the_creator(self):
        for rec in self:
            if rec.employee_id.user_id.id == rec.create_uid.id:
                rec.is_the_creator = True
    @api.model
    def create(self, vals):
        res = super(HrHolidaysExtension, self).create(vals)
        vals['name'] = self.env['ir.sequence'].get('hr.holidays.extension.seq')
        res.write(vals)
        return res
    
    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft' and self._uid != SUPERUSER_ID:
                raise ValidationError(u'لا يمكن حذف طلب إلغاء الإجازة فى هذه المرحلة يرجى مراجعة مدير النظام')
        return super(HrHolidaysExtension, self).unlink()
 
    @api.constrains('holiday_status_id')
    def check_constrains(self):
        current_holiday_status_stock = self.env['hr.employee.holidays.stock'].search([('employee_id', '=', self.employee_id.id),('holiday_status_id', '=', self.holiday_status_id.id)]).holidays_available_stock
        if current_holiday_status_stock>0:
            raise ValidationError(u'لا يمكن تمديد إجازة قبل إنتهاء رصيدها')
        for en in self.holiday_status_id.entitlements:
            if en.entitlment_category.id == self.env.ref('smart_hr.data_hr_holiday_entitlement_all').id:
                right_entitlement = en
            extension_period =  right_entitlement.extension_period
            open_period = self.env['hr.holidays'].check_holiday_periode_existance(self.employee_id,self.holiday_status_id,right_entitlement)
    
            old_extensions = self.search([('holiday_status_id','=',self.holiday_status_id),('state', '=', 'done'),
                                               ('employee_id', '=', self.employee_id.id),
                                                ('date', '>=', fields.Datetime.from_string(open_period.date_from))])
            sum_days = 0
            for extension in old_extensions:
                sum_days += extension.duration
            if extension_period*365 < sum_days+self.duration:
                raise ValidationError(u'ليس لديك الرصيد الكافي للتمديد')
                
        @api.one
        def button_send(self):
            user = self.env['res.users'].browse(self._uid)
            for extension in self:
                extension.state = 'audit'
                # send notification for requested the DM
                if self.is_the_creator: 
                    self.env['base.notification'].create({'title': u'إشعار بتمديد إجازة',
                                                      'message': u'الرجاء مراجعة طلب اتمديد',
                                                      'user_id': self.employee_id.parent_id.user_id.id,
                                                  'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                  'res_model':'hr.holidays.extension',
                                                  'res_id': self.id,
                                                  })
            else:
                # send notification for requested employee
                res_model = 'smart_hr.action_hr_holidays_cancellation_employees'
                self.env['base.notification'].create({'title':  u'إشعار بتمديد إجازة',
                                                  'message': u'الرجاء مراجعة طلب اتمديد',
                                                  'user_id': self.employee_id.user_id.id,
                                                  'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                  'res_model':'hr.holidays.extension',
                                                  'res_id': self.id,
                                                  'res_action': res_model})
                
            extension.message_post(u"تم إرسال الطلب من قبل '" + unicode(user.name) + u"'")

    @api.one
    def button_done(self):
        for extension in self:
            holidays_available_stock = self.env['hr.employee.holidays.stock'].search([('employee_id', '=', self.employee_id.id),
                                                           ('holiday_status_id', '=', self.holiday_status_id.id)]).holidays_available_stock

            holidays_available_stock+=extension.duration
            extension.state = 'done'

    @api.one
    def button_refuse(self):
        for extension in self:
            extension.state = 'refuse'
                # send notification for requested the DM
            self.env['base.notification'].create({'title': u'إشعار برفض تمديد إجازة',
                                                  'message': u' '+self.employee_id.name +u'لقد تم الرفض من قبل ',
                                                  'user_id': self.employee_id.parent_id.user_id.id,
                                                  'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                  'res_model':'hr.holidays.extension',
                                                  'res_id': self.id,
                                                  })

    @api.model
    def _needaction_domain_get(self):
        return [
            ('state', 'in', ['audit']),
        ]

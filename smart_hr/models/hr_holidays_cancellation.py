# -*- coding: utf-8 -*-

from openerp import fields, models, api, _
from openerp.exceptions import ValidationError
from openerp.tools import SUPERUSER_ID
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from datetime import date, datetime, timedelta

class hrHolidaysCancellation(models.Model):
    _name = 'hr.holidays.cancellation'
    _description = 'Holidays Cancellation'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'id desc'

    name = fields.Char(string=u'رقم القرار', advanced_search=True)
    date = fields.Date(string=u'تاريخ الطلب', default=fields.Datetime.now())
    employee_id = fields.Many2one('hr.employee',  string=u'الموظف', domain=[('employee_state','=','employee')], advanced_search=True)
    is_the_creator = fields.Boolean(string='Is Current User', compute='_employee_is_the_creator')
    
    holidays = fields.One2many('hr.holidays', 'holiday_cancellation', string=u'الإجازات')
    state = fields.Selection([
        ('draft', u'طلب'),
        ('audit', u'مراجعة'),
        ('done', u'إعتمد'),
        ('refuse', u'رفض'),
    ], string=u'حالة', default='draft', advanced_search=True)
    type = fields.Selection([
        ('cut', u'قطع'),
        ('cancellation', u'إلغاء'),
    ], string=u'نوع', default='cancellation', advanced_search=True)
    note = fields.Text(string = u'الملاحظات', required = True)
    
    @api.depends('employee_id')
    def _employee_is_the_creator(self):
        for rec in self:
            if rec.employee_id.user_id.id == rec.create_uid.id:
                rec.is_the_creator = True
    @api.model
    def create(self, vals):
        res = super(hrHolidaysCancellation, self).create(vals)
        vals = {}
        if self._context['operation'] == 'cancel':
            vals['type'] = 'cancellation'
        if self._context['operation'] == 'cut':
            vals['type'] = 'cut'
        vals['name'] = self.env['ir.sequence'].get('hr.holidays.cancellation.seq')
        res.write(vals)
        return res

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft' and self._uid != SUPERUSER_ID:
                raise ValidationError(u'لا يمكن حذف طلب إلغاء الإجازة فى هذه المرحلة يرجى مراجعة مدير النظام')
        return super(hrHolidaysCancellation, self).unlink()
 
    @api.constrains('holidays')
    def check_constrains(self):
        
        for holiday in self.holidays:
            if self._context['operation'] == 'cancel':
                if not holiday.holiday_status_id.can_be_cancelled:
                    raise ValidationError(u'نوع الاجازة '+holiday.holiday_status_id.name+u' لا يكن الغاؤها.')
                if holiday.is_started:
                        raise ValidationError(u'لا يمكن إلغاء إجازة قد بدأت.')
            if self._context['operation'] == 'cut':
                if not holiday.is_started:
                    raise ValidationError(u'لا يمكن قطع إجازة لم تبدأ بعد.')
                if holiday.holiday_status_id == self.env.ref('smart_hr.data_hr_holiday_status_normal'):
                    start_date = fields.Date.from_string(holiday.date_from)
                    now = fields.Date.from_string(fields.Datetime.now())
                    duration = (now - start_date).days + 1
                    if duration < 5:
                        raise ValidationError(u'لا يمكن قطع إجازة عادية قبل مرور خمسة أيام من بدئها.')

    @api.one
    def button_send(self):
        user = self.env['res.users'].browse(self._uid)
        for cancellation in self:
            cancellation.state = 'audit'
            # send notification for requested the DM
            if self.is_the_creator: 
                self.env['base.notification'].create({'title': u'إشعار بإلغاء أو قطع إجازة',
                                                  'message': u'الرجاء مراجعة طلب الإلغاء أو القطع',
                                                  'user_id': self.employee_id.parent_id.user_id.id,
                                                  'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                  'res_model':'hr.holidays.cancellation',
                                                  'res_id': self.id,
                                                  })
            else:
                # send notification for requested employee
                if self._context['operation'] == 'cancel':
                    res_model = 'smart_hr.action_hr_holidays_cancellation_employees'
                else:
                    res_model = 'smart_hr.action_hr_holidays_cut_employees'
                self.env['base.notification'].create({'title': u'إشعار بإلغاء أو قطع إجازة',
                                                  'message': u'الرجاء مراجعة طلب الإلغاء أو القطع',
                                                  'user_id': self.employee_id.user_id.id,
                                                  'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                  'res_model':'hr.holidays.cancellation',
                                                  'res_id': self.id,
                                                  'res_action': res_model})
                
            cancellation.message_post(u"تم إرسال الطلب من قبل '" + unicode(user.name) + u"'")

    @api.one
    def button_done(self):
        for cancellation in self:
            if cancellation.type=='cancellation':
                for holiday in cancellation.holidays:
                    for holiday_balance in holiday.employee_id.holidays_balance:
                        if holiday_balance.holiday_status_id.id == holiday.holiday_status_id.id:
                            holiday_balance.holidays_available_stock += holiday.duration
                            holiday_balance.token_holidays_sum -= holiday.duration
                            break    
                    if holiday.holiday_status_id.id  in [self.env.ref('smart_hr.data_hr_holiday_status_exceptional').id]:
                        holiday.open_period.holiday_stock += holiday.duration
                        # Update the holiday state
                    holiday.write({'state': 'cancel'})

            if cancellation.type=='cut':
                for holiday in cancellation.holidays:
                    for holiday_balance in holiday.employee_id.holidays_balance:
                        end_date = fields.Date.from_string(holiday.date_to)
                        now = fields.Date.from_string(fields.Datetime.now())
                        cuted_duration = (end_date - now).days
                        if holiday_balance.holiday_status_id.id == holiday.holiday_status_id.id:
                            holiday_balance.holidays_available_stock += cuted_duration
                            holiday_balance.token_holidays_sum -= cuted_duration
                            break
                    if holiday.holiday_status_id.id  in [self.env.ref('smart_hr.data_hr_holiday_status_exceptional').id]:
                        holiday.open_period.holiday_stock += cuted_duration
                    holiday.write({'state': 'cancel'})
                                    
            cancellation.state = 'done'

    @api.one
    def button_refuse(self):
        for cancellation in self:
            for holiday in cancellation.holidays:
                cancellation.state = 'draft'
                # send notification for requested the DM
                self.env['base.notification'].create({'title': u'إشعار برفض إلغاء أو قطع إجازة',
                                                  'message': u' '+self.employee_id.name +u'لقد تم الرفض من قبل ',
                                                  'user_id': self.employee_id.parent_id.user_id.id,
                                                  'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                  'res_model':'hr.holidays.cancellation',
                                                  'res_id': self.id,
                                                  })

    @api.model
    def _needaction_domain_get(self):
        return [
            ('state', 'in', ['audit']),
        ]

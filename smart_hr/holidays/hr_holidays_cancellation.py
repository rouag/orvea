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

    name = fields.Char(string=u'رقم القرار', )
    date = fields.Date(string=u'تاريخ الطلب', default=fields.Datetime.now())
    employee_id = fields.Many2one('hr.employee',  string=u'الموظف', domain=[('employee_state','=','employee')],  required=1)
    is_the_creator = fields.Boolean(string='Is Current User', compute='_employee_is_the_creator')
    
    holiday_id = fields.Many2one('hr.holidays' ,string=u'الإجازة')
    state = fields.Selection([
        ('draft', u'طلب'),
        ('audit', u'مراجعة'),
        ('done', u'إعتمد'),
        ('refuse', u'رفض'),
    ], string=u'حالة', default='draft', )
    type = fields.Selection([
        ('cut', u'قطع'),
        ('cancellation', u'إلغاء'),
    ], string=u'نوع', default='cancellation', )
    note = fields.Text(string = u'الملاحظات', required = True)
    
    def _employee_is_the_creator(self):
        for rec in self:
            if self.env.user.id == rec.create_uid.id:
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
                    for en in cancellation.holiday_id.holiday_status_id.entitlements:
                        right_entitlement = False
                        if not cancellation.holiday_id.entitlement_type:
                            entitlement_type = self.env.ref('smart_hr.data_hr_holiday_entitlement_all')
                        else:
                            entitlement_type = cancellation.holiday_id.entitlement_type
                        for en in cancellation.holiday_id.holiday_status_id.entitlements:
                            if en.entitlment_category.id == entitlement_type.id:
                                right_entitlement = en
                                break
                    for holiday_balance in cancellation.holiday_id.employee_id.holidays_balance:
                        if holiday_balance.holiday_status_id.id == cancellation.holiday_id.holiday_status_id.id and holiday_balance.entitlement_id.id == right_entitlement.id:
                            holiday_balance.holidays_available_stock += cancellation.holiday_id.duration
                            holiday_balance.token_holidays_sum -= cancellation.holiday_id.duration
                            break
                    if cancellation.holiday_id.open_period:
                        cancellation.holiday_id.open_period.holiday_stock += cancellation.holiday_id.duration
                        # Update the holiday state
                    cancellation.holiday_id.write({'state': 'cancel'})
                    if cancellation.holiday_id.holiday_status_id == self.env.ref('smart_hr.data_hr_holiday_status_study'):
                        study_followup = self.env['courses.followup'].search([('employee_id','=','holiday.employee_id.id'),
                                                                              ('state','=','progress'),
                                                                              ('holiday_id','=','holiday.id'),
                                                                              ])
                        if study_followup:
                            study_followup.state='cancel'
            if cancellation.type=='cut':
                    for holiday_balance in cancellation.holiday_id.employee_id.holidays_balance:
                        end_date = fields.Date.from_string(cancellation.holiday_id.date_to)
                        now = fields.Date.from_string(fields.Datetime.now())
                        cuted_duration = (end_date - now).days
                        if holiday_balance.holiday_status_id.id == cancellation.holiday_id.holiday_status_id.id:
                            holiday_balance.holidays_available_stock += cuted_duration
                            holiday_balance.token_holidays_sum -= cuted_duration
                            cancellation.holiday_id.duration -= cuted_duration
                            break
                        
                    if cancellation.holiday_id.open_period:
                        cancellation.holiday_id.open_period.holiday_stock += cuted_duration
                    cancellation.holiday_id.write({'state': 'cutoff'})
#                     type = " قطع"+" " +holiday.holiday_status_id.name.encode('utf-8')
#                     self.env['hr.employee.history'].sudo().add_action_line(self.employee_id, self.name, self.date, type)
                    if cancellation.holiday_id.holiday_status_id == self.env.ref('smart_hr.data_hr_holiday_status_study'):
                        study_followup = self.env['courses.followup'].search([('employee_id','=','holiday.employee_id.id'),
                                                                              ('state','=','progress'),
                                                                              ('holiday_id','=','holiday.id'),
                                                                              ])
                        if study_followup:
                            study_followup.state='cut'
            cancellation.state = 'done'

    @api.one
    def button_refuse(self):
        for cancellation in self:
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

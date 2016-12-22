# -*- coding: utf-8 -*-

from openerp import fields, models, api, _
from openerp.exceptions import ValidationError
from openerp.tools import SUPERUSER_ID
from lxml import etree

class hrHolidaysCancellation(models.Model):
    _name = 'hr.holidays.cancellation'
    _description = 'Holidays Cancellation'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _order = 'id desc'

    name = fields.Char(string=u'رقم القرار', advanced_search=True)
    date = fields.Date(string=u'تاريخ الطلب', default=fields.Datetime.now())
    holiday = fields.Many2one('hr.holidays', string=u'الإجازة')
    employee_id = fields.Many2one('hr.employee', related='holiday.employee_id', string=u'الموظف', advanced_search=True)
    is_current_user = fields.Boolean(string='Is Current User', related='holiday.is_current_user')
    state = fields.Selection([
        ('draft', u'طلب'),
        ('employee', u'مراجعة الموظف'),
        ('done', u'إعتمد'),
        ('refuse', u'رفض'),
    ], string=u'حالة', default='draft', advanced_search=True)
    type = fields.Selection([
        ('cut', u'طلب'),
        ('cancellation', u'مراجعة الموظف'),
    ], string=u'نوع', default='cancellation', advanced_search=True)
    
    
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

    @api.constrains('holiday')
    def check_constrains(self):
        
        if self._context['operation'] == 'cut' and self.holiday.holiday_status_id == self.env.ref('smart_hr.data_hr_holiday_status_normal'):
                start_date = fields.Date.from_string(self.holiday.date_from)
                now = fields.Date.from_string(fields.Datetime.now())
                duration = (now - start_date).days + 1
                if duration < 5:
                    raise ValidationError(u'لا يمكن قطع إجازة عادية قبل مرور خمسة أيام من بدئها.')
        
    @api.one
    def button_dm_send(self):
        user = self.env['res.users'].browse(self._uid)
        for cancellation in self:
            cancellation.state = 'employee'
            cancellation.message_post(u"تم إرسال الطلب من قبل '" + unicode(user.name) + u"'")

    @api.one
    def button_employee_done(self):
        for cancellation in self:
            cancellation.state = 'done'
            # Update the holiday state
            cancellation.holiday.state = 'cancel'

    @api.one
    def button_refuse(self):
        for cancellation in self:
            cancellation.state = 'draft'

    @api.model
    def _needaction_domain_get(self):
        return [
            ('state', 'in', ['employee']),
        ]
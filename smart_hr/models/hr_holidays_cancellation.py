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
    employee_id = fields.Many2one('hr.employee',  string=u'الموظف', domain=[('employee_state','=','employee')], advanced_search=True)
    holidays = fields.One2many('hr.holidays', 'holiday_cancellation', string=u'الإجازات')
    state = fields.Selection([
        ('draft', u'طلب'),
        ('employee', u'مراجعة الموظف'),
        ('done', u'إعتمد'),
        ('refuse', u'رفض'),
    ], string=u'حالة', default='draft', advanced_search=True)
    type = fields.Selection([
        ('cut', u'قطع'),
        ('cancellation', u'إلغاء'),
    ], string=u'نوع', default='cancellation', advanced_search=True)
    note = fields.Text(string = u'الملاحظات', required = True)
    
#     @api.depends('employee_id')
#     def _get_holidays(self):
#         for rec in self:
#             if rec._context['operation'] == 'cancel':
#                 # get only the none started holidays
#                 self.holidays = (0,0,rec.env['hr.holidays'].search([('employee_id.id', '=', rec.employee_id.id), ('is_started', '=', False),('state', '=', 'done')]))
#             if rec._context['operation'] == 'cut':
#                 # get all confirmed holidays
#                 self.holidays = (0,0,rec.env['hr.holidays'].search([('employee_id.id', '=', rec.employee_id.id), ('state', '=', 'done')]))
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
    def button_dm_send(self):
        user = self.env['res.users'].browse(self._uid)
        for cancellation in self:
            cancellation.state = 'employee'
            cancellation.message_post(u"تم إرسال الطلب من قبل '" + unicode(user.name) + u"'")

    @api.one
    def button_employee_done(self):
        for cancellation in self:
            for holiday in cancellation.holidays:
                # Update the holiday state
                holiday.write({'state': 'cancel'})
                # update holidays balance
                holiday._compute_balance(holiday.employee_id)
            cancellation.state = 'done'

    @api.one
    def button_refuse(self):
        for cancellation in self:
            for holiday in cancellation.holidays:
                holiday.state = 'draft'

    @api.model
    def _needaction_domain_get(self):
        return [
            ('state', 'in', ['employee']),
        ]

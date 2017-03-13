# -*- coding: utf-8 -*-
####################################
### This Module Created by smart_etech ###
####################################

from openerp import fields, models, api, _
from openerp.exceptions import ValidationError
from openerp.tools import SUPERUSER_ID
from umalqurra.hijri_date import HijriDate

class hr_suspension_end(models.Model):
    _name = 'hr.suspension.end'
    _inherit = ['ir.needaction_mixin']
    _description = 'Suspension Ending'

    name = fields.Char(string=u'رقم  إجراء إنهاء كف اليد', )
    date = fields.Date(string=u'التاريخ', default=fields.Datetime.now())
    employee_id = fields.Many2one('hr.employee', string=u'الموظف', )
    letter_sender = fields.Char(string=u'جهة الخطاب', )
    letter_no = fields.Char(string=u'رقم الخطاب', )
    letter_date = fields.Date(string=u'تاريخ الخطاب', default=fields.Datetime.now())
    release_date = fields.Date(string=u'تاريخ إطلاق السراح', default=fields.Datetime.now())
    release_reason = fields.Text(string=u'سبب إطلاق السراح')
    suspension_id = fields.Many2one('hr.suspension', string=u'قرار كف اليد')
    state = fields.Selection([
        ('draft', u'طلب'),
        ('hrm', u'مدير شؤون الموظفين'),
        ('done', u'اعتمدت'),
        ('refuse', u'رفض'),
    ], string=u'الحالة', default='draft', )
    condemned = fields.Boolean(string=u'‫صدر‬ في حقه‬ عقوبة‬', default=False)
    sentence = fields.Integer(string=u'مدة العقوبة (بالأيام)')

    @api.model
    def create(self, vals):
        ret = super(hr_suspension_end, self).create(vals)
        # Sequence
        vals = {}
        vals['name'] = self.env['ir.sequence'].get('hr.suspension.end.seq')
        ret.write(vals)
        return ret

    @api.multi
    def unlink(self):
        # Validation
        for rec in self:
            if rec.state != 'draft' and self._uid != SUPERUSER_ID:
                raise ValidationError(u'لا يمكن حذف قرار إنهاء كف اليد فى هذه المرحلة يرجى مراجعة مدير النظام')
        return super(hr_suspension_end, self).unlink()

    @api.one
    def button_hrm(self):
        for rec in self:
            rec.state = 'hrm'

    @api.multi
    def button_done(self):
        self.ensure_one()
        self.employee_id.employee_state = 'employee'
        if self.condemned:
            release_date = fields.Date.from_string(self.release_date)
            suspension_date = fields.Date.from_string(self.suspension_id.suspension_date)
            duration = (release_date-suspension_date).days
            self.env['hr.employee.promotion.history'].decrement_promotion_duration(self.employee_id,duration)
            self.employee_id.service_duration-= duration
            holiday_balance = self.env['hr.employee.holidays.stock'].search ([('employee_id', '=', self.employee_id.id),
                                                           ('holiday_status_id', '=', self.env.ref('smart_hr.data_hr_holiday_status_normal').id),
                                                                         ])
            holidays_available_stock = holiday_balance.holidays_available_stock  - duration
            holiday_balance.write({'holidays_available_stock':  holidays_available_stock})
        self.suspension_id.write({'suspension_end_id': self.id})
        self.state = 'done'
        
    @api.one
    def button_refuse(self):
        for rec in self:
            rec.state = 'refuse'

    ''' Report Functions '''

    def get_ummqura(self, g_date):
        try:
            g_date = fields.Date.from_string(g_date)
            hijri_date = HijriDate(g_date.year, g_date.month, g_date.day, gr=True)
            hijri_date_str = "{0}/{1}/{2}".format(int(hijri_date.year), int(hijri_date.month), int(hijri_date.day))
            return hijri_date_str
        except Exception:
            return False

    def get_hindi_nums(self, string_number):
        return string_number

    @api.multi
    def create_report_attachment(self):
        self.env['report'].get_pdf(self, 'smart_hr.hr_suspension_end_report')

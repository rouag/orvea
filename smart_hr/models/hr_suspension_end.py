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

    name = fields.Char(string=u'رقم القرار', advanced_search=True)
    date = fields.Date(string=u'التاريخ', default=fields.Datetime.now())
    employee_id = fields.Many2one('hr.employee', string=u'الموظف', advanced_search=True)
    letter_sender = fields.Char(string=u'جهة الخطاب', advanced_search=True)
    letter_no = fields.Char(string=u'رقم الخطاب', advanced_search=True)
    letter_date = fields.Date(string=u'تاريخ الخطاب', default=fields.Datetime.now())
    release_date = fields.Date(string=u'تاريخ إطلاك السراح', default=fields.Datetime.now())
    release_reason = fields.Text(string=u'سبب إطلاق السراح')
    suspension_id = fields.Many2one('hr.suspension', string=u'قرار كف اليد')
    state = fields.Selection([
        ('draft', u'طلب'),
        ('hrm', u'مدير شؤون الموظفين'),
        ('done', u'اعتمدت'),
        ('refuse', u'رفض'),
    ], string=u'الحالة', default='draft', advanced_search=True)

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

    @api.one
    def button_done(self):
        for rec in self:
            rec.employee_id.emp_state = 'working'
            rec.state = 'done'
        self.create_report_attachment()

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

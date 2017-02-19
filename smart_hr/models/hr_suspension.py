# -*- coding: utf-8 -*-
####################################
### This Module Created by smart-eteck ###
####################################

from openerp import fields, models, api, _
from openerp.exceptions import ValidationError
from openerp.tools import SUPERUSER_ID
from umalqurra.hijri_date import HijriDate

class hr_suspension(models.Model):
    _name = 'hr.suspension'
    _inherit = ['mail.thread', 'ir.needaction_mixin']
    _description = 'Suspension Decision'

    name = fields.Char(string=u' رقم إجراء كف اليد', advanced_search=True)
    date = fields.Date(string=u'التاريخ', default=fields.Datetime.now())
    employee_id = fields.Many2one('hr.employee', string=u'الموظف', advanced_search=True)
    employee_state = fields.Selection([('new', u'جديد'),
                                       ('waiting', u'في إنتظار الموافقة'),
                                       ('update', u'إستكمال البيانات'),
                                       ('done', u'اعتمدت'),
                                       ('refused', u'رفض'),
                                       ('employee', u'موظف')], string=u'الحالة', related='employee_id.employee_state')
    letter_sender = fields.Char(string=u'جهة الخطاب', advanced_search=True)
    letter_number = fields.Integer(string=u'رقم الخطاب', advanced_search=True)
    letter_date = fields.Date(string=u'تاريخ الخطاب')
    suspension_date = fields.Date(string=u'تاريخ الإيقاف')
    suspension_attachment = fields.Binary(string=u'الصورة الضوئية للقرار', attachment=True)
    raison = fields.Text(string=u'سبب كف اليد', advanced_search=True)
    suspension_end_id = fields.Many2one('hr.suspension.end', string=u'قرار إنهاء كف اليد')
    state = fields.Selection([
        ('draft', u'طلب'),
        ('hrm', u'مدير شؤون الموظفين'),
        ('done', u'اعتمدت'),
        ('refuse', u'رفض'),
    ], string=u'الحالة', default='draft', advanced_search=True)
    
    def num2hindi(self,string_number):
        if string_number:
            hindi_numbers = {'0':'٠','1':'١','2':'٢','3':'٣','4':'٤','5':'٥','6':'٦','7':'٧','8':'٨','9':'٩','.':','}
            if isinstance(string_number, unicode):
                hindi_string = string_number.encode('utf-8','replace')
            else:
                hindi_string = str(string_number)
            for number in hindi_numbers:
                hindi_string = hindi_string.replace(str(number),hindi_numbers[number])
            return hindi_string
    
    @api.model
    def create(self, vals):
        ret = super(hr_suspension, self).create(vals)
        # Sequence
        vals = {}
        vals['name'] = self.env['ir.sequence'].get('hr.suspension.seq')
        ret.write(vals)
        return ret

    @api.multi
    def unlink(self):
        # Validation
        for rec in self:
            if rec.state != 'draft' and self._uid != SUPERUSER_ID:
                raise ValidationError(u'لا يمكن حذف قرار كف اليد فى هذه المرحلة يرجى مراجعة مدير النظام')
        return super(hr_suspension, self).unlink()

#     @api.constrains('employee_id')
#     def check_employee_id(self):
#         for rec in self:
#             if rec.employee_id.emp_state != 'working':
#                 raise ValidationError(u"هذا الموظف ليس على رأس العمل حتى يكف يده")

    @api.one
    def button_hrm(self):
        user = self.env['res.users'].browse(self._uid)
        for rec in self:
            rec.state = 'hrm'
            rec.message_post(u"تم إرسال الطلب من قبل '" + unicode(user.name) + u"'")

    @api.one
    def button_done(self):
        user = self.env['res.users'].browse(self._uid)
        for rec in self:
            rec.employee_id.emp_state = 'suspended'
            rec.state = 'done'
            rec.message_post(u"تم الإعتماد من قبل '" + unicode(user.name) + u"'")
            rec.create_report_attachment()

    @api.one
    def button_refuse(self):
        for rec in self:
            rec.state = 'refuse'

    @api.one
    def button_suspension_end(self):
        # Objects
        susp_end_obj = self.env['hr.suspension.end']
        user = self.env['res.users'].browse(self._uid)
        # Create suspension end
        for rec in self:
            # Validation
            if not rec.suspension_end_id:
                vals = {
                    'employee_id': rec.employee_id.id,
                    'suspension_id': rec.id,
                }
                susp_end_id = susp_end_obj.create(vals)
                if susp_end_id:
                    rec.suspension_end_id = susp_end_id
                    rec.message_post(u"تم إنهاء كف اليد من قبل '" + unicode(user.name) + u"'")

    @api.model
    def _needaction_domain_get(self):
        return [
            ('state', '=', 'hrm'),
        ]

    """
        Report Functions
    """

    def get_ummqura(self, g_date):
        try:
            g_date = fields.Date.from_string(g_date)
            hijri_date = HijriDate(g_date.year, g_date.month, g_date.day, gr=True)
            hijri_date_str = "{0}/{1}/{2}".format(int(hijri_date.year), int(hijri_date.month), int(hijri_date.day))
            return self.num2hindi(hijri_date_str)
        except Exception:
            return False

    def get_hindi_nums(self, string_number):
        return self.num2hindi(string_number)

    def reverse_string(self, string):
        if string:
            return str(string)[::-1]

    @api.multi
    def create_report_attachment(self):
        self.env['report'].get_pdf(self, 'smart_hr.hr_suspension_report')

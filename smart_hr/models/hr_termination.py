# -*- coding: utf-8 -*-
####################################
### This Module Created by smart-etech ###
####################################

from openerp import fields, models, api, _
from openerp.exceptions import ValidationError
from openerp.tools import SUPERUSER_ID

class hr_termination(models.Model):
    _name = 'hr.termination'
    _inherit = ['ir.needaction_mixin']
    _description = 'Termination'

    name = fields.Char(string=u'رقم القرار', advanced_search=True)
    date = fields.Date(string=u'تاريخ', default=fields.Datetime.now())
    termination_date = fields.Date(string=u'تاريخ الإعتماد')
    employee_id = fields.Many2one('hr.employee', string=u'الموظف', advanced_search=True)
    employee_state = fields.Selection([('new', u'جديد'),
                                       ('waiting', u'في إنتظار الموافقة'),
                                       ('update', u'إستكمال البيانات'),
                                       ('done', u'اعتمدت'),
                                       ('refused', u'رفض'),
                                       ('employee', u'موظف')], string=u'الحالة', related='employee_id.employee_state')
    # Employee Info
    employee_no = fields.Integer(string=u'رقم الموظف', related='employee_id.employee_no')
    job_id = fields.Many2one(string=u'الوظيفة', related='employee_id.job_id')
    join_date = fields.Date(string=u'تاريخ الالتحاق بالجهة', related='employee_id.join_date')
    age = fields.Integer(string=u'السن', related='employee_id.age')
    # Termination Info
    termination_type_id = fields.Many2one('hr.termination.type', string=u'نوع الطى', advanced_search=True)
    reason = fields.Char(string=u'السبب')
    letter_source = fields.Char(string=u'جهة الخطاب', advanced_search=True)
    letter_no = fields.Char(string=u'رقم الخطاب', advanced_search=True)
    letter_date = fields.Date(string=u'تاريخ الخطاب')
    file_attachment = fields.Binary(string=u'مرفق الصورة الضوئية')
    file_attachment_name = fields.Char(string=u'مرفق الصورة الضوئية')
    state = fields.Selection([
        ('draft', u'طلب'),
        ('hrm', u'مدير شؤون الموظفين'),
        ('done', u'اعتمدت'),
        ('refuse', u'رفض'),
    ], string=u'الحالة', default='draft', advanced_search=True)

    @api.model
    def create(self, vals):
        ret = super(hr_termination, self).create(vals)
        # Sequence
        vals = {}
        vals['name'] = self.env['ir.sequence'].get('hr.term.seq')
        ret.write(vals)
        return ret

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft' and self._uid != SUPERUSER_ID:
                raise ValidationError(u'لا يمكن حذف طى القيد فى هذه المرحلة يرجى مراجعة مدير النظام')
        return super(hr_termination, self).unlink()

    @api.constrains('employee_id')
    def check_employee_id(self):
        for ter in self:
            if self.search_count([('employee_id', '=', ter.employee_id.id), ('state', '=', 'done')]):
                raise ValidationError(u"هذا الموظف تم أعتماد طى قيد لديه من قبل")

    @api.one
    def button_hrm(self):
        for ter in self:
            ter.state = 'hrm'

    @api.one
    def button_done(self):
        for ter in self:
            # Update Employee State
            ter.employee_id.emp_state = 'terminated'
            # Update Job
            ter.employee_id.job_id.employee_id = False
            ter.employee_id.job_id = False
            # Update State
            ter.state = 'done'
            # Set the termination date with the date of the final approve
            ter.termination_date = fields.Date.today()
        self.create_report_attachment()

    @api.one
    def button_refuse(self):
        for ter in self:
            ter.state = 'refuse'

    @api.model
    def _needaction_domain_get(self):
        return [
            ('state', '=', 'hrm'),
        ]

    """
    Report Methods
    """
    @api.multi
    def create_report_attachment(self):
        self.env['report'].get_pdf(self, 'smart_hr.hr_termination_report')


class hr_termination_type(models.Model):
    _name = 'hr.termination.type'
    _description = 'Termination Type'

    name = fields.Char(string=u'اسم')
    code = fields.Char(string=u'الرمز')
    nb_salaire = fields.Float(string=u'عدد الرواتب المستحق')
    all_holidays = fields.Boolean(string=u'كل الإجازة')
    max_days = fields.Float(string=u'الحد الاقصى لأيام الإجازة')
    
  
    
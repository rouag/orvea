# -*- coding: utf-8 -*-
####################################
### This Module Created by smart-etech ###
####################################

from openerp import fields, models, api, _
from openerp.exceptions import ValidationError
from openerp.tools import SUPERUSER_ID
from datetime import date, datetime, timedelta


class hr_termination(models.Model):
    _name = 'hr.termination'
    _order = 'id desc'
    _inherit = ['ir.needaction_mixin']
    _description = 'Termination'

    name = fields.Char(string=u'مسمى طي القيد', required=1)
    date = fields.Date(string=u'تاريخ', default=fields.Datetime.now())
    date_termination = fields.Date(string=u'تاريخ طي القيد  ', default=fields.Datetime.now())
    termination_date = fields.Date(string=u'تاريخ الإعتماد')
    employee_id = fields.Many2one('hr.employee', string=u'الموظف',  required=1)
    employee_state = fields.Selection([('new', u'جديد'),
                                       ('waiting', u'في إنتظار الموافقة'),
                                       ('update', u'إستكمال البيانات'),
                                       ('done', u'اعتمدت'),
                                       ('refused', u'رفض'),
                                       ('employee', u'موظف')], string=u'الحالة', related='employee_id.employee_state')
    # Employee Info
    employee_no = fields.Char(related='employee_id.number')
    job_id = fields.Many2one(string=u'الوظيفة', related='employee_id.job_id')
    join_date = fields.Date(string=u'تاريخ الالتحاق بالجهة', related='employee_id.join_date')
    age = fields.Integer(string=u'السن', related='employee_id.age')
    country_id = fields.Many2one(related='employee_id.country_id', store=True, readonly=True, string='الجنسية')
    # Termination Info
    termination_type_id = fields.Many2one('hr.termination.type', string=u'نوع الطي', )
    nb_salaire = fields.Float(related='termination_type_id.nb_salaire', store=True, readonly=True, string=u'عدد الرواتب المستحق')
    all_holidays = fields.Boolean(related='termination_type_id.all_holidays', store=True, readonly=True,string=u'كل الإجازة')
    max_days = fields.Float(related='termination_type_id.max_days', store=True, readonly=True, string=u'الحد الاقصى لأيام الإجازة')
    
    reason = fields.Char(string=u'السبب')
    letter_source = fields.Char(string=u'جهة الخطاب', )
    letter_no = fields.Char(string=u'رقم الخطاب',  required=1)
    letter_date = fields.Date(string=u'تاريخ الخطاب')
    file_attachment = fields.Binary(string=u'مرفق الصورة الضوئية', attachment=True)
    file_attachment_name = fields.Char(string=u'مرفق الصورة الضوئية')
    state = fields.Selection([
        ('draft', u'طلب'),
        ('hrm', u'مدير شؤون الموظفين'),
        ('done', u'اعتمدت'),
        ('refuse', u'رفض'),
    ], string=u'الحالة', default='draft', advanced_search=True)


    @api.onchange('termination_type_id')
    def _onchange_termination_type_id(self):

        if self.employee_id.country_id != self.env.ref('base.sa'):
                for rec in self.termination_type_id: 
                    rec.nb_salaire = 0 
                    rec.all_holidays = 0
                    rec.max_days = 0
                    rec.nationality = True  

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft' and self._uid != SUPERUSER_ID:
                raise ValidationError(u'لا يمكن حذف طي القيد فى هذه المرحلة يرجى مراجعة مدير النظام')
        return super(hr_termination, self).unlink()

#     @api.constrains('employee_id')
#     def check_employee_id(self):
#         for ter in self:
#             if self.search_count([('employee_id', '=', ter.employee_id.id), ('state', '=', 'done')]):
#                 raise ValidationError(u"هذا الموظف تم أعتماد طي قيد لديه من قبل")

    @api.multi
    def check_constraintes(self):
        if self.termination_type_id.years>0:
            if self.employee_id.age < self.termination_type_id.years:
                raise ValidationError(u" السن الادنى  هو %s سنة"%self.termination_type_id.years)
 
        if self.termination_type_id.evaluation_condition:
            years_progress = self.termination_type_id.years_progress
            for year in range(1,years_progress):
                employee_evaluation_id = self.env['hr.employee.evaluation.level'].search([('employee_id', '=', self.employee_id.id),('year', '=',date.today().year-year)], limit=1)
                if employee_evaluation_id:
                    if employee_evaluation_id.degree_id.id not in self.termination_type_id.evaluation_required.ids:
                        raise ValidationError(u"الرجاء مراجعة تقييم وظيفي خاص لنوع طي القيد")
                else:
                    raise ValidationError(u"لا يوجد تقييم وظيفي خاص بالموظف ل%sسنة"%years_progress)


    @api.multi
    def button_hrm(self):
        self.ensure_one()
        self.check_constraintes()
        self.state = 'hrm'

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
    nationality = fields.Boolean(string=u'غير سعودي')
    contract = fields.Boolean(string=u'متعاقد')
    evaluation_condition = fields.Boolean(string=u'يطبق شرط تقييم الأداء')
    years_progress = fields.Integer(string=u'عدد سنوات التقيم')
    evaluation_required = fields.Many2many('hr.evaluation.result.foctionality', string=u'التقييمات المطلوبة')
    include_members = fields.Boolean(string=u'تشمل اعضاء الهيئة')
    years = fields.Integer(string=u'السن')

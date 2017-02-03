# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import Warning
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from datetime import date, datetime, timedelta

class hr_promotion(models.Model):
    _name = 'hr.promotion'
    _inherit = ['ir.needaction_mixin']
    _description = 'Promotion Decision'

    name = fields.Char(string=u'رقم القرار', advanced_search=True)
    date = fields.Date(string=u'تاريخ الطلب', default=fields.Datetime.now())
    letter_sender = fields.Char(string=u'جهة الخطاب', advanced_search=True)
    letter_number = fields.Char(string=u'رقم الخطاب', advanced_search=True)
    letter_date = fields.Date(string=u'تاريخ الخطاب')
    commitee_report_number = fields.Char(string=u'رقم محضر لجنة الترقيات')
    commitee_report_date = fields.Date(string=u'تاريخ محضر لجنة الترقيات')
    old_job_id = fields.Many2one('hr.job', string=u'الوظيفة الحالية')
    new_job_id = fields.Many2one('hr.job', string=u'الوظيفة المرقى عليها')
    employee_id = fields.Many2one('hr.employee', string=u'الموظف')
    old_number_job = fields.Char(string='رقم الوظيفة', store=True, readonly=1) 
    new_number_job = fields.Char(string='رقم الوظيفة', store=True, readonly=1) 
    emp_department_id = fields.Many2one('hr.department', string='الادارة', store=True, readonly=1)
    emp_grade_id_old = fields.Many2one('salary.grid.grade', string='المرتبةالحالية ', store=True, readonly=1)
    emp_grade_id_new = fields.Many2one('salary.grid.grade', string='المرتبة الجديدة', store=True, readonly=1)
    promotion_type=fields.Selection([
        ('seniority', u'الأقدمية'),
        ('job_vide', u'شغور وظيفة'),
        ('appropriate_expertise', u'الخبرات المناسبة'),
    ], string=u'نوع الترقية', default='seniority', advanced_search=True)
    working_date = fields.Date(string=u'تاريخ مباشرة الوظيفة الجديدة')
    state = fields.Selection([
                              ('draft', u'طلب'),
                              ('employee_done', u'موافقة صاحب الترقية'),
                              ('manager', u'صاحب صلاحية التعين'),
                              ('minister', u'وزارة الخدمة المدنية'),
                              ('hrm', u'شؤون الموظفين'),
                              ('done', u'اعتمدت'),
                              ('refuse', u'رفض'),
                              ('cancel', u'ملغاة'),
                              ], string=u'حالة', default='draft', advanced_search=True)
# 
#     @api.model
#     def create(self, vals):
#         ret = super(hr_promotion, self).create(vals)
#         # Sequence
#         vals = {}
#         vals['name'] = self.env['ir.sequence'].get('hr.promotion.seq')
#         ret.write(vals)
#         return ret

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft' and self._uid != SUPERUSER_ID:
                raise ValidationError(u'لا يمكن حذف قرار الترقية في هذه المرحلة يرجى مراجعة مدير النظام')
        return super(hr_promotion, self).unlink()

    @api.onchange('employee_id')
    def _information_job(self):
        self.old_job_id=self.employee_id.job_id
        self.old_number_job = self.employee_id.job_id.number
        self.emp_grade_id_old = self.employee_id.job_id.grade_id.id
        self.department_id = self.employee_id.job_id.department_id.id
    
    @api.onchange('new_job_id')
    def _new_job(self):
        self.new_number_job = self.employee_id.job_id.number
        self.emp_grade_id_old = self.employee_id.job_id.grade_id.id
        self.department_id = self.employee_id.job_id.department_id.id
    @api.one
    def button_demande_employee(self):
        self.state = 'employee_done'   

class hr_promotion_type(models.Model):
    _name = 'hr.promotion.type'
     
    name = fields.Char(string=u'نوع الترقية', advanced_search=True)
    
 

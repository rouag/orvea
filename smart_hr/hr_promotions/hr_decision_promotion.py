# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import Warning
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from datetime import date, datetime, timedelta


class HrDecisionPromotion(models.Model):
    _name = 'hr.decision.promotion'
    _inherit = ['mail.thread']
    _description = u'قرار الترقية'

    name = fields.Char(string='رقم قرار الترقية', required=1, states={'draft': [('readonly', 0)]})
    order_date = fields.Date(string='تاريخ القرار', required=1)
    date_promotion = fields.Date(string='تاريخ الترقية', default=fields.Datetime.now(), )
    date_direct_action = fields.Date(string='تاريخ مباشرة العمل', required=1)
    employee_decision = fields.Boolean(string=u'مباشر', default=False)
    # info about employee
    employee_id = fields.Many2one('hr.employee', string='الموظف', required=1)
    number = fields.Char(string='الرقم الوظيفي', readonly=1)
    emp_code = fields.Char(string=u'رمز الوظيفة ', readonly=1)
    country_id = fields.Many2one(related='employee_id.country_id', store=True, readonly=True, string='الجنسية')
    emp_job_id = fields.Many2one('hr.job', string='الوظيفة', store=True, readonly=1)
    new_job_id = fields.Many2one('hr.job', string='الوظيفة', store=True, readonly=1)
    new_number_job = fields.Char(string='رقم الوظيفة', store=True, readonly=1)
    new_type_id = fields.Many2one('salary.grid.type', string='الصنف', store=True, readonly=1)
    emp_department_id = fields.Many2one('hr.department', string='الادارة', store=True, readonly=1)
    emp_grade_id = fields.Many2one('salary.grid.grade', string='المرتبة', store=True, readonly=1)
    emp_far_age = fields.Float(string=' السن الاقصى', store=True, readonly=1)
    emp_basic_salary = fields.Float(string='الراتب الأساسي', store=True, readonly=1)
    emp_degree_id = fields.Many2one('salary.grid.degree', string='الدرجة', store=True, readonly=1)
    # info about job
    job_id = fields.Many2one('hr.job', string='الوظيفة', required=1)
    number_job = fields.Char(string='رقم الوظيفة', readonly=1)
    code = fields.Char(string=u'رمز الوظيفة ', readonly=1)
    type_id = fields.Many2one('salary.grid.type', string='الصنف', readonly=1)
    department_id = fields.Many2one('hr.department', string='الادارة', readonly=1)
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة', readonly=1)
    degree_id = fields.Many2one('salary.grid.degree', string='الدرجة', required=1)
    # other info
    type_appointment = fields.Many2one('hr.type.appoint', string=u'نوع الترقية ',
                                       default=lambda self: self.env.ref('smart_hr.data_hr_recrute_agent_public'),
                                       )
    description = fields.Text(string=' ملاحظات ')

    state = fields.Selection([
        ('draft', u'طلب'),
        ('waiting', u'مقابلة شخصية'),
        ('manager', u'صاحب صلاحية التعين'),
        ('direct', u'مدير مباشر'),
        ('budget', u'رئيس الهيئة'),
        ('hrm', u'شؤون الموظفين'),
        ('done', u'اعتمدت'),
        ('refuse', u'رفض'),
        ('cancel', u'ملغاة'),
    ], string=u'الحالة', default='draft', )


class HrDecisionPromotionLine(models.Model):
    _name = 'hr.decision.promotion.line'
    _inherit = ['mail.thread']
    _description = u'قائمة الموظفين المؤهلين للترقية'


class HrTypeAppoint(models.Model):
    _name = 'hr.type.promotion'
    _description = u' أنواع الترقية  '

    name = fields.Char(string='قائمة الموظفين المؤهلين للترقية', required=1)
    date_test = fields.Char(string='فترة التجربة')
    code = fields.Char(string='الرمز')
    audit = fields.Boolean(string=u'تدقيق', default=False)
    recrutment_manager = fields.Boolean(string=u'موافقة صاحب صلاحية التعين ', default=True)
    enterview_manager = fields.Boolean(string=u'مقابلة شخصية', default=True)
    personnel_hr = fields.Boolean(string=u'شؤون الموظفين', default=True)
    direct_manager = fields.Boolean(string=u'  موافقة مدير مباشر ', default=True)
    recrutment_decider = fields.Boolean(string=u' موافقة رئيس الهيئة  ', default=True)
    can_be_cancelled = fields.Boolean(string=u'يمكن الغاؤها', default=True)

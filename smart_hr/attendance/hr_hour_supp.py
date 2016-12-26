# -*- coding: utf-8 -*-
####################################
### This Module Created by smart-etech ###
####################################

from openerp import fields, models, api, _
from openerp.exceptions import ValidationError
from openerp.tools import SUPERUSER_ID

class hrHourSupp(models.Model):
    _name = 'hr.hour.supp'
    _inherit = ['ir.needaction_mixin']

    name = fields.Char(string=u'رقم طلب الساعات الاضافية', advanced_search=True)
    date = fields.Date(string=u'تاريخ الطلب', default=fields.Datetime.now())
    termination_date = fields.Date(string=u'تاريخ الإعتماد')
    employee_id = fields.Many2one('hr.employee', string=u'الموظف', advanced_search=True)
    # Employee Info
    employee_no = fields.Integer(string=u'رقم الموظف', related='employee_id.employee_no')
    job_id = fields.Many2one(string=u'الوظيفة', related='employee_id.job_id')
#     level = fields.Char(string=u'المرتبة', related='employee_id.job_id.salary_ladder_id.salary_ladder_level_name')
#     degree = fields.Char(string=u'الدرجة', related='employee_id.job_id.salary_ladder_id.name')
    hour_supp_date = fields.Date(string=u'تاريخ الساعات الاضافية')
    hours = fields.Integer(string=u'الساعات الاضافية', )
    hours_leave = fields.Integer(string=u'ساعة الدخول', )
    hours_rentre = fields.Integer(string=u'ساعة الخروج', )
    
    # Termination Info
    reason = fields.Char(string=u'السبب')

    state = fields.Selection([
        ('draft', u'طلب'),
        ('hrm', u'مدير شؤون الموظفين'),
        ('done', u'اعتمدت'),
        ('refuse', u'رفض'),
    ], string=u'الحالة', default='draft', advanced_search=True)

 

    @api.one
    def button_hrm(self):
        for permission in self:
            permission.state = 'hrm'

    @api.one
    def button_done(self):
        for permission in self:
            permission.state = 'done'
            permission.termination_date = fields.Date.today()
           
         

    @api.one
    def button_refuse(self):
        for permission in self:
            permission.state = 'refuse'



   
# -*- coding: utf-8 -*-
####################################
### This Module Created by smart-etech ###
####################################

from openerp import fields, models, api, _
from openerp.exceptions import ValidationError
from openerp.tools import SUPERUSER_ID

class hr_permission(models.Model):
    _name = 'hr.permission'
    _inherit = ['ir.needaction_mixin']
    _description = 'permission'

    name = fields.Char(string=u'رقم طلب الاستئذان', advanced_search=True)
    date = fields.Date(string=u'تاريخ الطلب', default=fields.Datetime.now())
    termination_date = fields.Date(string=u'تاريخ الإعتماد')
    employee_id = fields.Many2one('hr.employee', string=u'الموظف', advanced_search=True)
    # Employee Info
    employee_no = fields.Integer(string=u'رقم الموظف', related='employee_id.employee_no')
    job_id = fields.Many2one(string=u'الوظيفة', related='employee_id.job_id')
#     level = fields.Char(string=u'المرتبة', related='employee_id.job_id.salary_ladder_id.salary_ladder_level_name')
#     degree = fields.Char(string=u'الدرجة', related='employee_id.job_id.salary_ladder_id.name')
    permission_date = fields.Date(string=u'تاريخ الاستئذان')
    hours = fields.Integer(string=u'مدة المغادرة بالساعة', )
    hours_leave = fields.Integer(string=u'ساعة الخروج', )
    hours_rentre = fields.Integer(string=u'ساعة الدخول', )
    
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



   
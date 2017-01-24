# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from openerp.exceptions import Warning
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from datetime import date, datetime, timedelta


class hrDirectAppoint(models.Model):
    _name = 'hr.direct.appoint'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string=' إسم الموظف', required=1)
    employee_id=fields.Many2one('hr.employee',string='الموظف',required=1)
    number=fields.Char(string='الرقم الوظيفي',readonly=1) 
    code = fields.Char(string=u'رمز الوظيفة ',readonly=1) 
    country_id=fields.Many2one(related='employee_id.country_id', store=True, readonly=True, string='الجنسية')
    job_id  = fields.Many2one('hr.job', string='الوظيفة',store=True,readonly=1) 
    number_job=fields.Char(string='رقم الوظيفة',store=True,readonly=1) 
    type_id=fields.Many2one('salary.grid.type',string='الصنف',store=True,readonly=1) 
    department_id=fields.Many2one('hr.department',string='القسم',store=True,readonly=1)
    grade_id=fields.Many2one('salary.grid.grade',string='المرتبة',store=True,readonly=1)
    far_age = fields.Float(string=' السن الاقصى',store=True,readonly=1) 
    basic_salary = fields.Float(string='الراتب الأساسي',store=True, readonly=1)   
    degree_id = fields.Many2one('salary.grid.degree', string='الدرجة',store=True, readonly=1)
    date_direct_action=fields.Date(string='تاريخ مباشرة العمل',required=1) 
    
    
    date = fields.Date(string=u'تاريخ المباشرة', default=fields.Datetime.now())
    state = fields.Selection([('new', ' ارسال طلب'),
                             ('waiting', 'في إنتظار الإعتماد'),
                             ('cancel', 'رفض'),
                             ('done', 'اعتمدت')], string='الحالة', readonly=1, default='new')


    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id :
            self.number = self.employee_id.number
            self.country_id = self.employee_id.country_id
            appoint_line = self.env['hr.decision.appoint'].search([('employee_id', '=', self.employee_id.id),('state','=','done'),('active', '=', True)],limit=1 )
            if appoint_line :
                
                self.job_id = appoint_line.job_id.id
                self.code = appoint_line.job_id.name.number
                self.number_job =appoint_line.number
                self.type_id = appoint_line.type_id.id
                self.far_age = appoint_line.type_id.far_age
                self.grade_id = appoint_line.grade_id.id
                self.department_id = appoint_line.department_id.id
                self.date_direct_action = appoint_line. date_direct_action
      
      
         
    
        
        
    @api.multi
    def action_waiting(self):
        date_direct_action = datetime.datetime.strptime(date_direct_action, "%m/%d/%y")
        print"date_direct_action",date_direct_action
        end_date = date_direct_action + datetime.timedelta(days=15)  
        print"end_date",end_date
        self.state = 'waiting'

    @api.one
    def action_cancel(self):
        self.state = 'cancel'

    @api.one
    def action_done(self):
        self.state = 'done'

    @api.one
    def action_refuse(self):
        self.state = 'new'
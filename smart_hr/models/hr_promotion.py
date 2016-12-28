# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning


class HrPromotion(models.Model):
    _name = 'hr.promotion'  
    _inherit = ['mail.thread'] 
    _description=u'الترقيات' 
    
    employee_id=fields.Many2one('hr.employee',string=' إسم الموظف',required=1,)
    number=fields.Char(string='الرقم الموظف',readonly=1) 
    #info about job
    job_id = fields.Many2one('hr.job', string=' المسمى الوظيفي ') 
    number_job=fields.Char(string='الرقم الوظيفي',readonly=1) 
    grade_id=fields.Many2one('salary.grid.grade',string='المرتبة',readonly=1)
    department_id=fields.Many2one('hr.department',string='القسم',readonly=1)
    job_day=fields.Char(string=' يوم') 
    job_month=fields.Char(string='شهر') 
    job_year=fields.Char(string=' سنة') 
    diplome=fields.Char(string=' أخر مؤهل حصل عليه والتخصص') 
    period=fields.Char(string=' المدة') 
    date=fields.Date(string='تاريخ ')
    direct=fields.Char(string=' مباشر') 
    not_direct=fields.Char(string='  غير مباشر') 
    education=fields.Char(string=' التعليم') 
    seniority=fields.Char(string='الأقدمية ')
    training=fields.Char(string=' التدريب') 
    evalution=fields.Char(string=' تقويم الأداء') 
    total_point=fields.Char(string='مجموع النقاط')
    deadline_sign=fields.Char(string=' تاريخ أخر موعد للتوقيع على الإقرار') 
    state= fields.Selection([('new','طلب'),('waiting','في إنتظار الإعتماد'),('done','اعتمدت')], readonly=1, default='new')

    
    @api.one
    def action_waiting(self):
        self.state = 'waiting' 
         
    @api.one
    def action_done(self):
        """
        TODO: update promotion history  for the employee when he have a promotion
        """
        self.state = 'done'  
        
    @api.one
    def action_refuse(self):
        self.state = 'new'   
        
    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id :
            self.number = self.employee_id.number 
    
    @api.onchange('job_id')
    def _onchange_job_id(self):
        if self.job_id :
            self.number_job = self.job_id.number
            self.grade_id = self.job_id.grade_id.id
            self.department_id = self.job_id.department_id.id


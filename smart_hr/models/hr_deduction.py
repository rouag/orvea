# -*- coding: utf-8 -*-

from openerp import models, api, fields, _
from openerp.exceptions import ValidationError

class hrDeductionType(models.Model):
    _name = 'hr.deduction.type'
    
    name=fields.Char(string=' الوصف',required=1)
    number=fields.Char(string='الرمز',required=1)
    
class hrDeduction(models.Model):
    _name = 'hr.deduction'
    
    
    name=fields.Char(string=' المسمى',required=1)
    number_decision=fields.Char(string='رقم القرار',required=1)
    date_decision=fields.Date(string=' تاريخ القرار',required=1)
    date=fields.Date(string=' التاريخ ',required=1,)
    state= fields.Selection([('new','جديدة'),('confirm','معتمدة')], readonly=1, default='new')
    line_ids = fields.One2many('hr.deduction.line', 'deduction_id',string='الحسميات',)
    line_history_ids = fields.One2many('hr.deduction.history', 'deduction_history_id',string='الحسميات',)
    
    @api.one
    def action_new(self):
        self.state = 'confirm' 
         
  
        
class hrDeductionLine(models.Model):
    _name = 'hr.deduction.line'
    
    deduction_id=fields.Many2one('hr.deduction',string=' الحسميات')
    employee_id=fields.Many2one('hr.employee',string=' إسم الموظف',required=1)
    number = fields.Char(related='employee_id.number', store=True, readonly=True,string=' الرقم الوظيفي')
    job_id = fields.Many2one(related='employee_id.job_id', store=True, readonly=True,string=' الوظيفة')
    department_id = fields.Many2one(related='employee_id.department_id', store=True, readonly=True,string=' القسم')
    deduction_type=fields.Many2one('hr.deduction.type',string='نوع الحسم',required=1)
    deduction_way= fields.Selection([('values','قيمة'),('day','أيام'),('hours','ساعات'),('rate','نسبة')],string='طريقة الحسم',required=1) 
    action_deduction=fields.Char(string='الإجراءات',)
    valuer_deduction=fields.Char(string='القيمة',required=1)
    premium_dedection=fields.Char(string='قسط الحسم',required=1)
    date_from=fields.Date(string='تاريخ من',required=1)
    date_to=fields.Date(string=' إلي',required=1)
    deduction_fixe=fields.Boolean(string='حسمية دائمة')
    
    
class hrDeductionHistory(models.Model):
    _name = 'hr.deduction.history'
    
    deduction_history_id=fields.Many2one('hr.deduction',string=' الحسميات')
    date_deduction=fields.Datetime(string=' التاريخ ',required=1)
    employee_id=fields.Many2one('hr.employee',string=' الموظف',required=1)
    reason=fields.Char(string=' السبب',required=1,)
    res_id=fields.Many2one('res.users',string=' صاحب الصلاحية',required=1)
    
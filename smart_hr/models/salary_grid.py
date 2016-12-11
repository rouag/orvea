# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning

class SalaryGrid(models.Model):
    _name = 'salary.grid'  
    _inherit = ['mail.thread']
    _description = u'سلّم الرواتب' 
    
    name = fields.Char(string='الإسم', required=1)
    numero_order = fields.Char(string='رقم القرار')
    date = fields.Date(string='التاريخ')
    enabled = fields.Boolean(string='مفعل')
    grid_ids = fields.One2many('salary.grid.detail', 'grid_id')
    
class SalaryGridType(models.Model):
    _name = 'salary.grid.type'  
    _description = u' الأصناف' 
    
    name = fields.Char(string='الصنف', required=1)   
    code = fields.Char(string='الرمز')   
    grid_id = fields.Many2one('salary.grid', string='سلّم الرواتب')
    
class SalaryGridGrade(models.Model):
    _name = 'salary.grid.grade'  
    _description = u'المراتب' 
    
    name = fields.Char(string='الإسم', required=1)  
    code = fields.Char(string='الرمز') 
    annual_premium = fields.Char(string=' العلاوة السنوية')   
    type_id = fields.Many2one('salary.grid.type', string='الصنف')

class SalaryGridDegree(models.Model):
    _name = 'salary.grid.degree'  
    _description = u'الدرجة' 
    
    name = fields.Char(string='الإسم', required=1)  
    code = fields.Char(string='الرمز') 
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة')

class SalaryGridDetail(models.Model):
    _name = 'salary.grid.detail'  
    _description = u'تفاصيل سلم الرواتب' 
      
    grid_id = fields.Many2one('salary.grid', string='سلّم الرواتب',required=1)   
    type_id = fields.Many2one('salary.grid.type', string='الصنف',required=1)  
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة',required=1) 
    degree_id = fields.Many2one('salary.grid.degree', string='الدرجة',required=1) 
    basic_salary = fields.Float(string='الراتب الأساسي',required=1)   
    transport_allow = fields.Float(string='بدل النقل') 
    retirement = fields.Float(string='المحسوم للتقاعد') 
    net_salary = fields.Float(string='صافي الراتب',required=1)
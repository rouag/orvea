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
    code = fields.Integer(string='الرمز')   
    basic_salary = fields.Float(string='الراتب الأساسي') 
    allowance_ids = fields.Many2many('hr.allowance',  string=u'البدلات' )
    far_age = fields.Float(string=' السن الاقصى',)
    code = fields.Char(string='الرمز')   
    reward_ids = fields.Many2many('hr.reward',  string=u'المكافآت‬' )
    grid_id = fields.Many2one('salary.grid', string='سلّم الرواتب')
    retrait_monthly = fields.Integer(string='نسبة الحسم الشهري على التقاعد:')   
    assurance_monthly = fields.Integer(string='نسبة التامين الشهري  من الراتب الاساسي:')   
    salary_recent = fields.Float(string=' أخر راتب شهري' ,invisible=True)
    
class SalaryGridGrade(models.Model):
    _name = 'salary.grid.grade'  
    _description = u'المراتب' 
    
    name = fields.Char(string='الإسم', required=1)  
    code = fields.Char(string='الرمز') 
    annual_premium = fields.Char(string=' العلاوة السنوية')   
    type_id = fields.Many2one('salary.grid.type', string='الصنف')
    job_create_id = fields.Many2one('hr.job.create', string=' وظائف')
    job_strip_from_id = fields.Many2one('hr.job.strip.from', string=' وظائف')

class SalaryGridDegree(models.Model):
    _name = 'salary.grid.degree'  
    _description = u'الدرجة' 
    
    name = fields.Char(string='الإسم', required=1)  
    code = fields.Char(string='الرمز') 
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة')
    sequence = fields.Integer(string='الترتيب')

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = '[%s] %s' % (record.code, record.name)
            result.append((record.id, name))
        return result

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
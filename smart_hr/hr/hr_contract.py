# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from openerp.exceptions import Warning
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from datetime import date


class HrContract(models.Model):
    _inherit = 'hr.contract'
    
    employee_id=fields.Many2one('hr.employee',string='الموظف',required=1,)
    country_id=fields.Many2one(related='employee_id.country_id', store=True, readonly=True, string='الجنسية')
    identification_id = fields.Char(related='employee_id.identification_id', store=True, readonly=True,string=u'رقم الهوية')
    identification_date=fields.Date(related='employee_id.identification_date', store=True, readonly=True,string=u'تاريخ إصدار بطاقة الهوية')
    identification_place=fields.Char(related='employee_id.identification_place', store=True, readonly=True,string=u'مكان إصدار بطاقة الهوية')
    calendar_id=fields.Many2one(related='employee_id.calendar_id', store=True, readonly=True,string=u'وردية العمل')
    passport_id=fields.Char(related='employee_id.passport_id', store=True, readonly=True,string=u'رقم جواز السفر')
    job_id=fields.Many2one('hr.job',string='المسمى الوظيفي',required=1,)
    department_id=fields.Many2one(related='employee_id.department_id', store=True, readonly=True,string='القسم',)
    assurance=fields.Char(string='التامين') 
    type_id=fields.Many2one('salary.grid.type',string='الصنف',readonly=1) 
    grade_id=fields.Many2one('salary.grid.grade',string='المرتبة',readonly=1)
    struct_id= fields.Many2one('hr.payroll.structure', 'Salary Structure',required=False)
    #struct_id= fields.Char(string="struct",required=0,),
    degree_id = fields.Many2one('salary.grid.degree', string='الدرجة' )
    payement_emploi = fields.Many2one('hr.contract.payement',string=' الدفع المجدول')
    date_to = fields.Date(string=u' من', )
    date_endd = fields.Date(string=u'إلى', )
    date_contract_to = fields.Date(string=u'من', )
    date_contract_end = fields.Date(string=u'إلى', )
    basic_salary = fields.Float(string='الراتب الأساسي',required=1)   
    transport_allow = fields.Float(string='بدل النقل') 
    retirement = fields.Float(string='المحسوم للتقاعد') 
    net_salary = fields.Float(string='صافي الراتب',required=1)
    contract_item_ids = fields.Many2many('hr.contract.item',  string=u'بند العقد')
    
   
    employee_id1=fields.Many2one('hr.employee',string='المسؤول على العقد',required=1,)
    job_id1=fields.Many2one(related='employee_id1.job_id', store=True, readonly=True,)
    employee_id2=fields.Many2one('hr.employee',string='مراجع البيانات',required=1,)
    job_id2=fields.Many2one(related='employee_id2.job_id', store=True, readonly=True,)
    department_id1=fields.Many2one(related='employee_id1.department_id', store=True, readonly=True,string='القسم',)
    department_id2=fields.Many2one(related='employee_id2.department_id', store=True, readonly=True,string='القسم',)
    renewable=fields.Boolean(string='قابل للتجديد')
    ticket_travel=fields.Boolean(string='تذاكر السفر')
    ticket_famely=fields.Boolean(string='تذكرة سفر عائلية')
    
    @api.onchange('state')
    def _onchange_state(self):
        if self.state == 'open':
            self.date_contract_to = fields.Datetime.now()
   
    @api.onchange('job_id')
    def _onchange_job_id(self):
        if self.job_id :
            self.type_id = self.job_id.type_id.id
            self.grade_id = self.job_id.grade_id.id
            
    @api.onchange('degree_id')
    def _onchange_degree_id(self):
            if self.degree_id:
           
                salary_grid_line = self.env['salary.grid.detail'].search([('type_id', '=', self.type_id.id),
                                                ('grade_id', '=', self.grade_id.id),
                                                  ('degree_id', '=', self.degree_id.id)
                                                ])
                if salary_grid_line:
                    self.basic_salary = salary_grid_line.basic_salary  
                    self.transport_allow = salary_grid_line.transport_allow
                    self.retirement = salary_grid_line.retirement
                    self.net_salary = salary_grid_line.net_salary
                    
                    
class hrContractPayement(models.Model):
    _name = 'hr.contract.payement'

    name = fields.Char(advanced_search=True,string=u'المسمّى')
    periode = fields.Char(string=u'المدة')
    

    
    
class hrContractItem(models.Model):
    _name = 'hr.contract.item'
    
    name = fields.Char(string=u'مسمى المادة')
    code = fields.Char(string=u'رقم المادة')
    text = fields.Html(string=u' محتوى المادة')
 #   contract_item=fields.Many2one('hr.contract.item',string='بند العقد')
    
# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning

class HrDecisionAppoint(models.Model):
    _name = 'hr.decision.appoint'  
    _inherit = ['mail.thread'] 
    _description=u'قرار تعيين'
    
    name=fields.Char(string='رقم القرار',required=1 ,states={'new': [('readonly', 0)]})
    order_date=fields.Date(string='تاريخ القرار',required=1) 
    date_hiring=fields.Date(string='تاريخ التعيين',required=1) 
    type_appointment=fields.Many2one('hr.type.appoint',string='نوع التعيين',required=1,states={'new': [('readonly', 0)]})
    date_direct_action=fields.Date(string='تاريخ مباشرة العمل',required=1) 
    instead_exchange=fields.Boolean(string='صرف بدل تعيين')
    #info about employee
    employee_id=fields.Many2one('hr.employee',string='الموظف',required=1,domain=[('employee_state','=','done')],states={'new': [('readonly', 0)]})
    number=fields.Char(string='الرقم الوظيفي',readonly=1) 
    country_id=fields.Many2one(related='employee_id.country_id', store=True, readonly=True, string='الجنسية')
    
    #info about job
    job_id = fields.Many2one('hr.job', string='الوظيفة') 
    number_job=fields.Char(string='الرقم الوظيفي',readonly=1) 
    
    type_id=fields.Many2one('salary.grid.type',string='الصنف',readonly=1) 
    department_id=fields.Many2one('hr.department',string='القسم',readonly=1)
    grade_id=fields.Many2one('salary.grid.grade',string='المرتبة',readonly=1)
   
    basic_salary = fields.Float(string='الراتب الأساسي',readonly=1)   
    transport_allow = fields.Float(string='بدل النقل',readonly=1) 
    retirement = fields.Float(string='المحسوم للتقاعد',readonly=1) 
    net_salary = fields.Float(string='صافي الراتب',readonly=1)
    #other info
    degree_id = fields.Many2one('salary.grid.degree', string='الدرجة', required=1)
    description=fields.Text(string=' ملاحظات ') 
    state= fields.Selection([('new','طلب'),('waiting','في إنتظار الإعتماد'),('done','اعتمدت')], readonly=1, default='new',) 
    #attachments files
    order_picture=fields.Binary(string='صورة القرار',required=1) 
    medical_examination_file = fields.Binary(string = 'وثيقة الفحص الطبي') 
    order_enquiry_file = fields.Binary(string = 'طلب الاستسفار')
    
    
    @api.one
    def action_waiting(self):
        self.state = 'waiting' 
         
    @api.multi
    def action_done(self):
        if not self.medical_examination_file or not self.order_enquiry_file:
            raise Warning(_('يجب عليك إرفاق كل من شهادة الفحص الطبي وطلب الاستسفار.'))
        #update employee data
        self.employee_id.job_id=self.job_id.id
        self.employee_id.department_id=self.department_id.id
        self.employee_id.employee_state='employee'
        self.state = 'done'
        # update holidays balance for the employee
        self.env['hr.holidays']._compute_balance(self.employee_id)
        # create promotion history line
        self.env['hr.employee.promotion.history'].create({'employee_id': self.employee_id.id, 'salary_grid_id': self.employee_id.job_id.grade_id.id, 'date_from': fields.Datetime.now() })
        
        #create system user and link current employee to created user
        if self.employee_id.work_email:
            user = self.env['res.users'].create({'name':self.employee_id.name,'login':self.employee_id.work_email, 'email':self.employee_id.work_email})
            self.employee_id.user_id = user
        else:
            raise Warning(_('الرجاء تعبئة البريد الإلكتروني.'))
         
    @api.one
    def action_refuse(self):
        self.state = 'new' 
        
    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id :
            self.number = self.employee_id.number
            self.country_id = self.employee_id.country_id
            self.job_id = self.employee_id.job_id
           

               
    @api.onchange('job_id')
    def _onchange_job_id(self):
        if self.job_id :
            self.number_job = self.job_id.number
            self.type_id = self.job_id.type_id.id
            self.grade_id = self.job_id.grade_id.id
            self.department_id = self.job_id.department_id.id
            
          #  self.basic_salary = self.job_id.basic_salary.id
           # self.transport_allow = self.job_id.transport_allow.id
           # self.retirement = self.job_id.retirement.id
           # self.net_salary = self.job_id.net_salary.id
            
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
                
               
class HrTypeAppoint(models.Model):
    _name = 'hr.type.appoint'  
    _description=u'أنواع التعين'
    
    
    name=fields.Char(string='النوع',required=1 )
    date_test=fields.Date(string='فترة التجربة') 
    code=fields.Char(string='الرمز')
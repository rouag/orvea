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
    type_appointment=fields.Char(string='نوع التعيين',required=1,states={'new': [('readonly', 0)]})
    date_direct_action=fields.Date(string='تاريخ مباشرة العمل',required=1) 
    instead_exchange=fields.Boolean(string='صرف بدل تعيين')
    #info about employee
    employee_id=fields.Many2one('hr.employee',string='الموظف',required=1,domain=[('state','=','done')],states={'new': [('readonly', 0)]})
    number=fields.Char(string='الرقم الوظيفي',readonly=1) 
    #info about job
    job_id = fields.Many2one('hr.job', string='الوظيفة') 
    number_job=fields.Char(string='الرقم الوظيفي',readonly=1) 
    type_id=fields.Many2one('salary.grid.type',string='الصنف',readonly=1) 
    department_id=fields.Many2one('hr.department',string='القسم',readonly=1)
    grade_id=fields.Many2one('salary.grid.grade',string='المرتبة',readonly=1)
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
        self.employee_id.state='employee'
        self.state = 'done'
        
        #create system user and link current employee to created user
        if self.employee_id.work_email:
            user = self.env['res.users'].create({'name':self.employee_id.name,'login':self.employee_id.work_email})
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
            self.job_id = self.employee_id.job_id
           
           
    @api.onchange('job_id')
    def _onchange_job_id(self):
        if self.job_id :
            self.number_job = self.job_id.number
            self.type_id = self.job_id.type_id.id
            self.grade_id = self.job_id.grade_id.id
            self.department_id = self.job_id.department_id.id

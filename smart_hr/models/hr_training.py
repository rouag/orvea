# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning


class HrTraining(models.Model):
    _name = 'hr.training'  
    _description=u'التدريب' 
    
    @api.one
    @api.depends('line_ids')
    def _compute_info(self):
        self.number_participant = len(self.line_ids)
        
    name=fields.Char(string=' الإسم',required=1,states={'new': [('readonly', 0)]})
    number=fields.Char(string='رقم القرار',required=1,states={'new': [('readonly', 0)]})
    date=fields.Date(string=' تاريخ القرار',required=1,states={'new': [('readonly', 0)]})
    date_of=fields.Date(string='تاريخ من',required=1,states={'new': [('readonly', 0)]})
    date_end=fields.Date(string=' إلى',required=1,states={'new': [('readonly', 0)]})
    period=fields.Float(string=' المدة',required=1,states={'new': [('readonly', 0)]})
    department=fields.Char(string=' الجهة',required=1,states={'new': [('readonly', 0)]})
    place=fields.Char(string=' المكان',required=1,states={'new': [('readonly', 0)]})
    number_place=fields.Integer(string='عدد المقاعد',required=1,states={'new': [('readonly', 0)]})
    number_participant=fields.Integer(string=' عدد المشتركين' ,store=True, readonly=True, compute='_compute_info')
    line_ids = fields.One2many('hr.candidates', 'employee_id',string='المترشحين',required=1,states={'new': [('readonly', 0)]})
    state= fields.Selection([('new','جديد'),('candidat','الترشح'),('review','المراجعة'),('confirm','إعتمدت'),('done','تمت')], readonly=1, default='new')
    employee_ids = fields.Many2many('hr.employee', 'employee_training_rel', 'emp_id', 'training_id', string=u'الموظفون') 

        
    @api.one
    def action_waiting(self):
        self.state = 'candidat' 
         
    @api.one
    def action_candidat(self):
        self.state = 'confirm'  
        
    @api.one
    def action_review(self):
        self.state = 'new'   
    @api.one
    def action_confirm(self):
        self.state = 'done'  
        
    @api.one
    def action_done(self):
        self.state = 'new'   
        
        
class HrCandidates(models.Model):
    _name = 'hr.candidates'  
    _description=u'المترشحين'
    
    employee_id=fields.Many2one('hr.employee',string=' إسم الموظف')
    number = fields.Char(related='employee_id.number', store=True, readonly=True,string=' الرقم الوظيفي')
    job_id = fields.Many2one(related='employee_id.job_id', store=True, readonly=True,string=' الوظيفة')
    department_id = fields.Many2one(related='employee_id.department_id', store=True, readonly=True,string=' القسم')
    training_id=fields.Many2one('hr.training',string=' الدورة')
    date_of = fields.Date(related='training_id.date_of', store=True, readonly=True)
    date_end = fields.Date(related='training_id.date_end', store=True, readonly=True)
    department = fields.Char(related='training_id.department', store=True, readonly=True)
    state= fields.Selection([('new','طلب'),('waiting','في إنتظار الإعتماد'),('done','اعتمدت')], readonly=1, default='new',) 
    
    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id :
            self.number = self.employee_id.number
            self.job_id = self.employee_id.job_id.id
            self.department_id = self.employee_id.department_id.id
                
    @api.onchange('training_id')
    def _onchange_training_id(self):
        if self.training_id :
            self.date_of = self.date_of
            self.date_end = self.date_end
            self.department = self.department
            
    @api.one
    def action_waiting(self):
        self.state = 'waiting' 
         
    @api.one
    def action_done(self):
        self.state = 'done'  
        
    @api.one
    def action_refuse(self):
        self.state = 'new'     
    
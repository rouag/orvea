# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from openerp.exceptions import Warning
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from datetime import date

class HrJob(models.Model):
    _inherit = 'hr.job'  
    _description = u'الوظائف'
   
    name = fields.Char(string='المسمى', required=1)
    number = fields.Char(string='الرقم الوظيفي', required=1, states={'unoccupied': [('readonly', 0)]})
    department_id = fields.Many2one('hr.department', string='الإدارة', required=1, states={'unoccupied': [('readonly', 0)]})
    genral_id = fields.Many2one('hr.groupe.job', ' المجموعة العامة', ondelete='cascade')
    specific_id = fields.Many2one('hr.groupe.job', ' المجموعة النوعية', ondelete='cascade')
    serie_id = fields.Many2one('hr.groupe.job', ' سلسلة الفئات', ondelete='cascade')
    type_id = fields.Many2one('salary.grid.type', string='التصنيف', required=1, states={'unoccupied': [('readonly', 0)]}) 
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة', required=1, states={'unoccupied': [('readonly', 0)]})
    state = fields.Selection([('unoccupied', 'شاغرة'), ('occupied', 'مشغولة'), ('cancel', 'ملغاة')], readonly=1, default='unoccupied')
    employee = fields.Many2one('hr.employee', string=u'الموظف')
    deputed_employee = fields.Boolean(string=u'موظف ندب', advanced_search=True)

    @api.multi
    def action_job_reservation(self):
        context = {};
        context['job_id'] = self.id
        return {
              'name': u'حجز الوظيفة',
              'view_type': 'form',
              "view_mode": 'form',
              'res_model': 'hr.job.reservation',
              'type': 'ir.actions.act_window',
              'context': context,
              'target': 'new',
              }
         
class HrJobReservation(models.Model):
    _name = 'hr.job.reservation'  
    _description = u'الوظائف'
    _rec_name = 'employee'
    
    employee = fields.Many2one('hr.employee', string=u'الموظف', required=1)
    
    @api.multi
    def action_job_reservation_confirm(self):
        if self.employee:
            self.env['hr.job'].search([('id', '=', self._context['job_id'])]).write({'employee':self.employee.id, 'state':'occupied'})
            self.employee.write({'job_id':self._context['job_id']})       
           
class HrJobCreate(models.Model):
    _name = 'hr.job.create'  
    _inherit = ['mail.thread']
    _description = u'إحداث وظائف'
    
    name = fields.Char(string='المسمى', required=1, readonly=1, states={'new': [('readonly', 0)]})
    speech_number = fields.Char(string='رقم الخطاب', required=1, readonly=1, states={'new': [('readonly', 0)]})
    speech_date = fields.Date(string='تاريخ الخطاب', required=1, readonly=1, states={'new': [('readonly', 0)]})
    speech_picture = fields.Binary(string='صورة الخطاب', required=1, readonly=1, states={'new': [('readonly', 0)]})
    line_ids = fields.One2many('hr.job.create.line', 'job_create_id', readonly=1, states={'new': [('readonly', 0)]})
    state = fields.Selection([('new', 'طلب'), ('waiting', 'في إنتظار الإعتماد'), ('done', 'اعتمدت')], readonly=1, default='new') 
    genral_id = fields.Many2one('hr.groupe.job', ' المجموعة العامة', ondelete='cascade')
    specific_id = fields.Many2one('hr.groupe.job', ' المجموعة النوعية', ondelete='cascade')
    serie_id = fields.Many2one('hr.groupe.job', ' سلسلة الفئات', ondelete='cascade')
    grade_ids = fields.One2many('salary.grid.grade','job_create_id', string='المرتبة',)
   
    @api.onchange('serie_id')
    def onchange_rank(self):
        if self.serie_id:
            gride=[]
            for classment in self.serie_id.hr_classment_job_ids:
                gride.append(classment.grade_id.id)
            self.grade_ids=gride
   
   
    @api.one
    def action_waiting(self):
        self.state = 'waiting'       

    @api.one
    def action_done(self):
        for line in self.line_ids:
            job_val = {'name': line.name,
                     'number': line.number,
                     'type_id':line.type_id.id,
                     'grade_id':line.grade_id.id,
                     'department_id':line.department_id.id,
                     'genral_id':self.genral_id.id,
                     'specific_id':self.specific_id.id,
                     'serie_id':self.serie_id.id,
                     
                     }
            self.env['hr.job'].create(job_val)
        self.state = 'done'  
             
    @api.one
    def action_refuse(self):
        self.state = 'new'        

class HrJobCreateLine(models.Model):
    _name = 'hr.job.create.line'  
    _description = u'الوظائف'
    
    name = fields.Char(string='الوظيفة', required=1)
    number = fields.Char(string='الرقم الوظيفي', required=1) 
    type_id = fields.Many2one('salary.grid.type', string='التصنيف', required=1) 
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة', required=1) 
    department_id = fields.Many2one('hr.department', string='الإدارة', required=1) 
    job_create_id = fields.Many2one('hr.job.create', string=' وظائف')
    _sql_constraints = [
        ('number_grade_uniq', 'unique(number,grade_id)', 'لا يمكن إضافة وظيفتين بنفس الرتبة والرقم'),
        ] 
    
class HrJobCancel(models.Model):
    _name = 'hr.job.cancel'  
    _inherit = ['mail.thread']    
    _description = u' إلغاء الوظائف'
    
    name = fields.Char(string='المسمى', required=1)
    speech_number = fields.Char(string='رقم الخطاب', required=1) 
    speech_date = fields.Date(string='تاريخ الخطاب', required=1) 
    speech_picture = fields.Binary(string='صورة الخطاب', required=1) 
    job_cancel_ids = fields.One2many('hr.job.cancel.line', 'job_cancel_line_id')
    state = fields.Selection([('new', 'طلب'), ('waiting', 'في إنتظار الإعتماد'), ('done', 'اعتمدت')], readonly=1, default='new') 
    
    @api.one
    def action_waiting(self):
        self.state = 'waiting' 
         
    @api.one
    def action_done(self):
        self.state = 'done'  
        for job in self.job_cancel_ids:
            job.job_id.state='cancel'
        
    @api.one
    def action_refuse(self):
        self.state = 'new'   
        
class HrJobCancelLine(models.Model):
    _name = 'hr.job.cancel.line'  
    _description = u'الوظائف'
    
    job_cancel_line_id = fields.Many2one('hr.job.cancel', string='الوظيفة', required=1) 
    job_id = fields.Many2one('hr.job', string='الوظيفة', required=1) 
    type_id = fields.Many2one('salary.grid.type', string='التصنيف', required=1,readonly=1) 
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة', required=1,readonly=1) 
    department_id = fields.Many2one('hr.department', string='الإدارة', required=1,readonly=1) 
    
    @api.onchange('job_id')
    def _onchange_job_id(self):
        if self.job_id :
            self.type_id = self.job_id.type_id.id
            self.grade_id = self.job_id.grade_id.id
            self.department_id = self.job_id.department_id.id
            
class HrJobMoveGrade(models.Model):
    _name = 'hr.job.move.grade'  
    _inherit = ['mail.thread']    
    _description = u'نقل وظائف'
    
    name = fields.Char(string='مسمى الوظيفة', required=1) 
    speech_number = fields.Char(string='رقم الخطاب', required=1) 
    speech_date = fields.Date(string='تاريخ الخطاب', required=1)
    speech_picture = fields.Binary(string='صورة الخطاب', required=1) 
    job_grade_ids = fields.One2many('hr.job.move.grade.line', 'job_grade_line_id')
    state = fields.Selection([('new', 'طلب'), ('waiting', 'في إنتظار الإعتماد'), ('done', 'اعتمدت')], readonly=1, default='new',) 
    
    @api.one
    def action_waiting(self):
        self.state = 'waiting' 
         
    @api.one
    def action_done(self):
        self.state = 'done' 
        for job in self.job_grade_ids:
            job.job_id.department_id=job.New_department_id.id 
        
    @api.one
    def action_refuse(self):
        self.state = 'new'          
    
class HrJobMoveGradeLine(models.Model):
    _name = 'hr.job.move.grade.line'  
    _description = u'نقل وظائف'
    
    job_id = fields.Many2one('hr.job', string='الوظيفة', required=1 ,) 
    type_id = fields.Many2one('salary.grid.type', string='التصنيف', readonly=1, required=1) 
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة ', readonly=1, required=1) 
    department_id = fields.Many2one('hr.department', string=' الإدارة الحالية', readonly=1, required=1) 
    New_department_id = fields.Many2one('hr.department', string='الإدارة الجديد', required=1) 
    job_grade_line_id = fields.Many2one('hr.job.move.grade', string='الوظيفة', required=1) 
    
    @api.onchange('job_id')
    def _onchange_job_id(self):
        if self.job_id :
            self.type_id = self.job_id.type_id.id
            self.grade_id = self.job_id.grade_id.id
            self.department_id = self.job_id.department_id.id
    
class HrJobMoveDeparrtment(models.Model):
    _name = 'hr.job.move.department'  
    _inherit = ['mail.thread']    
    _description = u'رفع أو خفض وظائف'
    
    name = fields.Char(string='مسمى الوظيفة', required=1) 
    speech_number = fields.Char(string='رقم الخطاب', required=1) 
    speech_date = fields.Date(string='تاريخ الخطاب', required=1) 
    speech_picture = fields.Binary(string='صورة الخطاب', required=1) 
    job_movement_ids = fields.One2many('hr.job.move.department.line', 'job_movement_line_id')
    state = fields.Selection([('new', 'طلب'), ('waiting', 'في إنتظار الإعتماد'), ('done', 'اعتمدت')], readonly=1, default='new')  
       
    @api.one
    def action_waiting(self):
        self.state = 'waiting' 
         
    @api.one
    def action_done(self):
        self.state = 'done'  
        for job in self.job_movement_ids:
            job.job_id.grade_id=job.new_grade_id.id
        
    @api.one
    def action_refuse(self):
        self.state = 'new'             
        
        
class HrJobMoveDeparrtmentLine(models.Model):
    _name = 'hr.job.move.department.line'  
    _description = u'رفع أو خفض وظائف'
    
    job_movement_line_id = fields.Many2one('hr.job.move.department', string='الوظيفة', required=1) 
    job_id = fields.Many2one('hr.job', string='الوظيفة', required=1) 
    type_id = fields.Many2one('salary.grid.type', string='التصنيف', readonly=1, required=1) 
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة الحالية', readonly=1, required=1) 
    new_grade_id = fields.Many2one('salary.grid.grade', string=' المرتبة الجديد', required=1) 
    department_id = fields.Many2one('hr.department', string='الإدارة', readonly=1, required=1) 
   
    @api.onchange('job_id')
    def _onchange_job_id(self):
        if self.job_id :
            self.type_id = self.job_id.type_id.id
            self.grade_id = self.job_id.grade_id.id
            self.department_id = self.job_id.department_id.id
    
class HrJobMoveUpdate(models.Model):
    _name = 'hr.job.update'  
    _inherit = ['mail.thread']    
    _description = u'تعديل وظائف'    
    
    name = fields.Char(string='مسمى الوظيفة', required=1) 
    speech_number = fields.Char(string='رقم الخطاب', required=1) 
    speech_date = fields.Date(string='تاريخ الخطاب', required=1) 
    speech_picture = fields.Binary(string='صورة الخطاب', required=1) 
    job_update_ids = fields.One2many('hr.job.update.line', 'job_update_line_id')
    state = fields.Selection([('new', 'طلب'), ('waiting', 'في إنتظار الإعتماد'), ('done', 'اعتمدت')], readonly=1, default='new') 
    
    @api.one
    def action_waiting(self):
        self.state = 'waiting' 
         
    @api.one
    def action_done(self):
        self.state = 'done'
        for job in self.job_update_ids:
            job.job_id.name=job.new_name
        
    @api.one
    def action_refuse(self):
        self.state = 'new'        
    
class HrJobMoveUpdateLine(models.Model):
    _name = 'hr.job.update.line'  
    _description = u'تحوير‬ وظيفة'
  
    job_update_line_id = fields.Many2one('hr.job.update', string='الوظيفة', required=1) 
    new_name = fields.Char(string='مسمى الجديد', required=1)
    job_id = fields.Many2one('hr.job', string='الوظيفة', required=1) 
    type_id = fields.Many2one('salary.grid.type', string='التصنيف', readonly=1, required=1) 
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة', readonly=1, required=1) 
    department_id = fields.Many2one('hr.department', string='الإدارة', readonly=1, required=1) 
     
    @api.onchange('job_id')
    def _onchange_job_id(self):
        if self.job_id :
            self.type_id = self.job_id.type_id.id
            self.grade_id = self.job_id.grade_id.id
            self.department_id = self.job_id.department_id.id
# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning


class HrEmployee(models.Model):
    _inherit = 'hr.employee'  
    
    number = fields.Char(string=u'الرقم الوظيفي', required=1) 
    working_hours_calendar = fields.Many2one('resource.calendar', string=u"الورديات")
    father_name = fields.Char(string=u'إسم الأب', required=1)
    is_resident = fields.Boolean (string=u'موظف مقيم', required=1) 
    birthday_location = fields.Char(string=u'مكان الميلاد')
    attachments = fields.Many2many('ir.attachment', 'res_id', string=u"المرفقات")
    recruiter = fields.Many2one('recruiter.recruiter', string=u'جهة التوظيف', required=1)
    state = fields.Selection([('new', u'جديد'),
                             ('waiting', u'في إنتظار الموافقة'),
                             ('update', u'إستكمال البيانات'),
                             ('done', u'اعتمدت'),
                             ('refused', u'رفض'),
                             ('employee', u'موظف')
                             ], string=u"الحالة", default='new')
    education_level = fields.Many2one('hr.employee.education.level', string = u'المستوى التعليمي')
     # Leaves Stock
    leave_normal = fields.Float(string=u'العادية', default=36)
    leave_emergency = fields.Float(string=u'الاضطرارية', default=5)
    leave_compensation = fields.Float(string=u'البديلة', default=0)

    
    
    @api.one
    @api.constrains('number','identification_id')
    def _check_constraints(self):
        if len(self.identification_id) != 10:
                    raise Warning(_('الرجاء التثبت من رقم الهوية.'))
                
        if len(self.search([('number', '=', self.number)])) > 1:
                    raise Warning(_('يوجد موظف لديه نفس الرقم التوظيفي.'))
    @api.one
    def action_send(self):
        self.state = 'waiting'  

    @api.one
    def action_confirm(self):
        self.state = 'done' 
        
    @api.one
    def action_cancel(self):
        self.state = 'new'
    
    @api.one
    def action_refuse(self):
        self.state = 'refused'          
                 
class HrJob(models.Model):
    _inherit = 'hr.job'  
    _description = u'الوظائف'
    
    
    name = fields.Char(string='المسمى', required=1)
    number = fields.Char(string='الرقم الوظيفي', required=1, states={'unoccupied': [('readonly', 0)]})
    department_id = fields.Many2one('hr.department', string='الإدارة', required=1, states={'unoccupied': [('readonly', 0)]})
    type_id = fields.Many2one('salary.grid.type', string='التصنيف', required=1, states={'unoccupied': [('readonly', 0)]}) 
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة', required=1, states={'unoccupied': [('readonly', 0)]})
    state = fields.Selection([('unoccupied', 'شاغرة'), ('occupied', 'مشغولة'), ('cancel', 'ملغاة')], readonly=1, default='unoccupied')
    employee = fields.Many2one('hr.employee', string=u'الموظف')
    
    
  
    
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
    
class HrJobCancel(models.Model):
    _name = 'hr.job.cancel'  
    _inherit = ['mail.thread']    
    _description = u'الوظائف'
    
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
        
    @api.one
    def action_refuse(self):
        self.state = 'new'   
        
class HrJobCancelLine(models.Model):
    _name = 'hr.job.cancel.line'  
    _description = u'الوظائف'
    
    job_cancel_line_id = fields.Many2one('hr.job.cancel', string='الوظيفة', required=1) 
    job_id = fields.Many2one('hr.job', string='الوظيفة', required=1) 
    type_id = fields.Many2one('salary.grid.type', string='التصنيف', required=1) 
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة', required=1) 
    department_id = fields.Many2one('hr.department', string='الإدارة', required=1) 
    
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
        
    @api.one
    def action_refuse(self):
        self.state = 'new'        
    
class HrJobMoveUpdateLine(models.Model):
    _name = 'hr.job.update.line'  
    _description = u'تعديل وظائف'
  
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
            
class HrEmployeeEducationLevel(models.Model):
    _name = 'hr.employee.education.level'  
    _description = u'مستويات التعليم'
  
    name = fields.Char(string = u'الإسم')
    code = fields.Char(string = u'الرمز')
    leave_type = fields.Many2one('hr.holidays.status', string='leave type')

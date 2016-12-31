# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from openerp.exceptions import Warning
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from datetime import date


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    number = fields.Char(string=u'الرقم الوظيفي', required=1)

    father_name = fields.Char(string=u'إسم الأب', required=1)
    is_resident = fields.Boolean(string=u'موظف مقيم', required=1)
    birthday_location = fields.Char(string=u'مكان الميلاد')
    attachments = fields.Many2many('ir.attachment', 'res_id', string=u"المرفقات")
    recruiter = fields.Many2one('recruiter.recruiter', string=u'جهة التوظيف', required=1)
    employee_state = fields.Selection([('new', u'جديد'),
                                       ('waiting', u'في إنتظار الموافقة'),
                                       ('update', u'إستكمال البيانات'),
                                       ('done', u'اعتمدت'),
                                       ('refused', u'رفض'),
                                       ('employee', u'موظف')], string=u'الحالة', default='new')
    education_level = fields.Many2one('hr.employee.education.level', string=u'المستوى التعليمي')
    # Deputation Stock
    deputation_stock = fields.Integer(string=u'الأنتدابات', default=60)
    service_years = fields.Integer(string=u'سنوات الخدمة', compute='_compute_service_years')
    emp_state = fields.Selection([('working', u'على رأس العمل'),
                                  ('suspended', u'مكفوف اليد'),
                                  ('terminated', u'مطوي قيده'),
                                  ], string=u'الحالة', default='working', advanced_search=True)
    job_id = fields.Many2one(advanced_search=True)
    age = fields.Integer(string=u'السن', compute='_compute_age')
    employee_no = fields.Integer(string=u'رقم الموظف', advanced_search=True)
    join_date = fields.Date(string=u'تاريخ الالتحاق بالجهة')
    external_decision = fields.Boolean(string=u'موافقة خارجية', default=False)
    holidays = fields.One2many('hr.holidays', 'employee_id', string=u'الاجازات')
    holidays_balance = fields.One2many('hr.employee.holidays.stock', 'employee_id', string=u'الأرصدة', readonly=1)
    promotions_history = fields.One2many('hr.employee.promotion.history', 'employee_id', string=u'الترقيات')
    traveling_ticket = fields.Boolean(string=u'تذكرة سفر', default=False)
    traveling_ticket_familiar = fields.Boolean(string=u'تذكرة سفر عائليّة', default=False)
    compensation_stock = fields.Integer(string=u'رصيد إجازات التعويض')
    sick_holiday_peiodes = fields.One2many('hr.illness.holidays.periode', 'employee_id', string='sick holidays periodes')
    
    def _compute_service_years(self):
        for emp in self:
            decision_appoint = self.env['hr.decision.appoint'].search([('state', '=', 'done'), ('employee_id', '=', emp.id)])
            if decision_appoint:
                today_date = fields.Date.from_string(fields.Date.today())
                date_hiring = fields.Date.from_string(decision_appoint[0].date_hiring)
                days = (today_date - date_hiring).days
                deductible_days = 0
                # find the holidays of the employee that are deductible_duration_service and promotion_deductible
                holidays = self.env['hr.holidays'].search([
                    ('state', '=', 'done'),
                    ('employee_id', '=', emp.id),
                    ('holiday_status_id.deductible_duration_service', '=', True), ('holiday_status_id.promotion_deductible', '=', True),
                    ])
                # find the holidays of the employee that are only promotion_deductible
                holidays += self.env['hr.holidays'].search([
                    ('state', '=', 'done'),
                    ('employee_id', '=', emp.id),
                    ('holiday_status_id.deductible_duration_service', '=', False), ('holiday_status_id.promotion_deductible', '=', True),
                    ])
                for holiday in holidays:
                    days -= holiday.duration
                years = days / 365
                if years > -1:
                    emp.service_years = years



    @api.depends('birthday')
    def _compute_age(self):
        for emp in self:
            if emp.birthday:
                today_date = fields.Date.from_string(fields.Date.today())
                birthday = fields.Date.from_string(emp.birthday)
                years = (today_date - birthday).days / 365
                if years > -1:
                    emp.age = years


    @api.one
    @api.constrains('number', 'identification_id')
    def _check_constraints(self):
        if len(self.identification_id) != 10:
                    raise Warning(_('الرجاء التثبت من رقم الهوية.'))
        if len(self.search([('number', '=', self.number)])) > 1:
                    raise Warning(_('يوجد موظف لديه نفس الرقم التوظيفي.'))
    @api.one
    def action_send(self):
        self.employee_state = 'waiting'  

    @api.one
    def action_confirm(self):
        self.employee_state = 'done' 
        
    @api.one
    def action_cancel(self):
        self.employee_state = 'new'
    
    @api.one
    def action_refuse(self):
        self.employee_state = 'refused'
    
    @api.multi 
    def button_my_info(self):
        employee = self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1)
        if employee:
            value = {
                'name': u'بياناتي',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'hr.employee',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'res_id': employee.id,
            }
            return value
        
class HrEmployeeHolidaysStock(models.Model):
    _name = 'hr.employee.holidays.stock'

    employee_id = fields.Many2one('hr.employee', string=u'الموظف')
    holiday_status_id = fields.Many2one('hr.holidays.status', string=u'نوع الاجازة')
    holidays_available_stock = fields.Float(string=u'رصيد الاجازة (يوم)')
    token_holidays_sum = fields.Integer(string=u'الإيام المأخوذة', default=0)
    periode = fields.Selection([
        (1, u'سنة'),
        (2, u'سنتين'),
        (3, u'ثلاث سنوات'),
        (4, u'أربع سنوات'),
        (5, u'خمس سنوات'),
        (6, u'ستة سنوات'),
        (7, u'سبعة سنوات'),
        (8, u'ثمانية سنوات'),
        (9, u'تسعة سنوات'),
        (10, u'عشرة سنوات'),
        ], string=u'مدة صلاحيات الإجازة', default=1) 

class HrEmployeePromotionHistory(models.Model):
    _name = 'hr.employee.promotion.history'

    employee_id = fields.Many2one('hr.employee', string=u' إسم الموظف')
    salary_grid_id = fields.Many2one('salary.grid.grade', string=u'الرتبة')
    date_from = fields.Date(string=u'التاريخ من', default=fields.Datetime.now())
    date_to = fields.Date(string=u'التاريخ الى')
    balance = fields.Integer(string=u'رصيد الترقية (يوم)', compute='_compute_balance',store=True)

    def _compute_balance(self):
        for rec in self:
            if rec.date_from:
                today_date = fields.Date.from_string(fields.Date.today())
                date_from = fields.Date.from_string(rec.date_from)
                days = (today_date - date_from).days
                # find the holidays of the employee start from date_from and they are promotion_deductible
                # only deductible_duration_service it means promotion_deductible also
                holidays = self.env['hr.holidays'].search([
                    ('state', '=', 'done'),
                    ('employee_id', '=', rec.employee_id.id),
                    ('holiday_status_id.deductible_duration_service', '=', True),
                    ('date_from', '>=', rec.date_from)
                    ])
                for holiday in holidays:
                    days -= holiday.periode

                rec.balance = days
 

                      
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
  
    name = fields.Char(string=u'الإسم')
    sequence = fields.Char(string=u'الرتبة')
    leave_type = fields.Many2one('hr.holidays.status', string='leave type')

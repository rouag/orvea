# -*- coding: utf-8 -*-



from openerp import models, fields, api, _
from openerp.exceptions import Warning
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from datetime import date, datetime, timedelta

class HrDecisionAppoint(models.Model):
    _name = 'hr.decision.appoint'  
    _inherit = ['mail.thread'] 
    _description = u'قرار تعيين'
    
    name = fields.Char(string='رقم القرار', required=1 , states={'draft': [('readonly', 0)]})
    order_date = fields.Date(string='تاريخ القرار', required=1) 
    date_hiring = fields.Date(string='تاريخ التعيين', default=fields.Datetime.now(),)
    date_hiring_end = fields.Date(string=u'تاريخ إنتهاء التعيين')  
    date_direct_action = fields.Date(string='تاريخ مباشرة العمل', required=1) 
    instead_exchange = fields.Boolean(string='صرف بدل تعيين')
    active = fields.Boolean(string=u'مفعل', default=True)
    # info about employee
    employee_id = fields.Many2one('hr.employee', string='الموظف', required=1)
    number = fields.Char(string='الرقم الوظيفي', readonly=1) 
    emp_code = fields.Char(string=u'رمز الوظيفة ', readonly=1) 
    country_id = fields.Many2one(related='employee_id.country_id', store=True, readonly=True, string='الجنسية')
    emp_job_id = fields.Many2one('hr.job', string='الوظيفة', store=True, readonly=1) 
    emp_number_job = fields.Char(string='رقم الوظيفة', store=True, readonly=1) 
    emp_type_id = fields.Many2one('salary.grid.type', string='الصنف', store=True, readonly=1) 
    emp_department_id = fields.Many2one('hr.department', string='القسم', store=True, readonly=1)
    emp_grade_id = fields.Many2one('salary.grid.grade', string='المرتبة', store=True, readonly=1)
    emp_far_age = fields.Float(string=' السن الاقصى', store=True, readonly=1) 
    emp_basic_salary = fields.Float(string='الراتب الأساسي', store=True, readonly=1)   
    emp_degree_id = fields.Many2one('salary.grid.degree', string='الدرجة', store=True, readonly=1)
    # info about job
    job_id = fields.Many2one('hr.job', string='الوظيفة', required=1)
    number_job = fields.Char(string='رقم الوظيفة', readonly=1) 
    code = fields.Char(string=u'رمز الوظيفة ', readonly=1) 
    type_id = fields.Many2one('salary.grid.type', string='الصنف', readonly=1) 
    department_id = fields.Many2one('hr.department', string='القسم', readonly=1)
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة', readonly=1)
    far_age = fields.Float(string=' السن الاقصى', readonly=1) 
    basic_salary = fields.Float(string='الراتب الأساسي', readonly=1)   
    transport_allow = fields.Float(string='بدل النقل', readonly=1) 
    retirement = fields.Float(string='المحسوم للتقاعد', readonly=1) 
    net_salary = fields.Float(string='صافي الراتب', readonly=1)
    salary_recent = fields.Float(string=' أخر راتب شهري ')
    transport_alocation = fields.Boolean(string='بدل نقل')
    transport_car = fields.Boolean(string='سيارة')
    degree_id = fields.Many2one('salary.grid.degree', string='الدرجة', required=1)
    # other info
    type_appointment = fields.Many2one('hr.type.appoint', string=u'نوع التعيين' , default=lambda self: self.env.ref('smart_hr.data_hr_recrute_agent_public'), advanced_search=True)
    description = fields.Text(string=' ملاحظات ') 
    state_appoint = fields.Selection([
                              ('active', u'مفعل'),
                              ('close', u'مغلق'),
                              ('refuse', u'ملغى'),
                              ('hanging', u'معلق'),
                              ('new', u'جديد'),
                              ], string=u' حالةالتعيين ', default='new', advanced_search=True)
    state = fields.Selection([
                              ('draft', u'طلب'),
                              ('audit', u'تدقيق'),
                              ('waiting', u'مقابلة شخصية'),
                            ('manager', u'صاحب صلاحية التعين'),
                             ('direct', u'مدير مباشر'),
                             ('budget', u'رئيس الهيئة'),
                              ('hrm', u'شؤون الموظفين'),
                              ('done', u'اعتمدت'),
                               ('refuse', u'رفض'),
                               ('cancel', u'ملغاة'),
                              ], string=u'حالة', default='draft', advanced_search=True)
    
    
   
    # attachments files
    order_picture = fields.Binary(string='صورة القرار', required=1) 
    medical_examination_file = fields.Binary(string='وثيقة الفحص الطبي') 
    order_enquiry_file = fields.Binary(string='طلب الاستسفار')
    file_salar_recent = fields.Binary(string='تعهد من الموظف')
    file_engagement = fields.Many2many('ir.attachment', string='إرفاق مزيد من الوثائق')
    # file_engagement = fields.Binary(string = 'تعهد من المترشح')
    file_appoint = fields.Binary(string='قرار التعين')
    file_decision = fields.Binary(string='قرار المباشر')
    
    @api.multi
    def send_appoint_request(self):
        self.ensure_one()
       
        if self.type_appointment.audit:
            self.message_post(u"تم إرسال الطلب من قبل '" + u"' إلى مدقق طلبات التعين")
            self.state = 'audit'
            
        elif self.type_appointment.enterview_manager:
            self.message_post(u"تم إرسال الطلب من قبل '" + u"' إلى مسؤول على مقابلة شخصية")
            self.state = 'waiting'
        elif self.type_appointment.recrutment_manager:
            self.message_post(u"تم إرسال الطلب من قبل '" + u"' إلى صاحب صلاحية التعين")
            self.state = 'manager'
        elif self.type_appointment.personnel_hr:
            self.message_post(u"تم إرسال الطلب من قبل '" + u"' إلى فريق الموارد البشرية")
            self.state = 'hrm'
        elif self.type_appointment.recrutment_decider:
            self.message_post(u"تم إرسال الطلب من قبل '" + u" إلى رئيس الهئية ")
            self.state = 'budget'
#             elif self.type_appointment == self.env.ref('sm
            
    # control audit group_audit_appointment
    @api.multi
    def button_accept_audit(self):
        self.ensure_one()
        if self.type_appointment.audit:
            self.state = 'waiting'
        else :
            self.state = 'draft'
        
    @api.multi
    def button_refuse_audit(self):
        self.ensure_one()
        if self.type_appointment.audit:
            self.state = 'draft'
    # control enterview manager  group_enterview_manager
    @api.multi
    def button_accept_enterview_manager(self):
        self.ensure_one()
        if self.type_appointment.enterview_manager:
            self.state = 'manager'
            
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تمت الموافقة من قبل '" + unicode(user.name) + u"'")    
    @api.multi
    def button_refuse_enterview_manager(self):
        self.ensure_one()
        if self.type_appointment.enterview_manager:
            self.state = 'refuse'
        
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تم الرفض من قبل '" + unicode(user.name) + u"'")
   # # control recrutment group_recrutment_manager
       
    @api.multi
    def button_accept_recrutment_manager(self):
        self.ensure_one()
        if self.type_appointment.recrutment_manager and self.type_appointment.recrutment_decider:
            self.state = 'budget'
        if  self.type_appointment.recrutment_manager and self.type_appointment.personnel_hr :
            self.state = 'hrm'
      
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تمت الموافقة من قبل '" + unicode(user.name) + u"'")
       # if self.employee_id.age > 60 :
          #  raise ValidationError(u"الرجاء التثبت من سن المترشح تجاوز 60)")
    
    @api.multi
    def button_refuse_recrutment_manager(self):
        self.ensure_one()
        if self.type_appointment.recrutment_manager:
            self.state = 'refuse'
        
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تم الرفض من قبل '" + unicode(user.name) + u"'")
    @api.multi
    def button_accept_recrutment_decider(self):
        self.ensure_one()
        if self.type_appointment.recrutment_decider and self.type_appointment.personnel_hr:
            self.state = 'hrm'
        if self.type_appointment.recrutment_decider :
             self.state = 'done'
        # Add to log
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تمت الموافقة من قبل '" + unicode(user.name) + u"'")
    
    @api.multi
    def button_refuse_recrutment_decider(self):
        self.ensure_one()
        if self.type_appointment.recrutment_decider:
            self.state = 'refuse'
        # Add to log
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تم الرفض من قبل '" + unicode(user.name) + u"'")
           
        
        
    # contyrol hr group_personnel_hr       
    @api.multi
    def button_accept_personnel_hr(self):
        self.ensure_one()
        if self.type_appointment.personnel_hr and self.type_appointment.direct_manager:
            self.state = 'direct'
        else :
            self.state = 'done'
            
            direct_appoint_obj = self.env['hr.direct.appoint']
            self.env['hr.direct.appoint'].create({'employee_id': self.employee_id.id,
                                                  'number' : self.number,
                                                  'country_id' : self.country_id.id,
                                                  'date_hiring' : self.date_hiring,
                                                  'type_id' : self.type_id.id,
                                                  'job_id' : self.job_id.id,
                                                   'number_job' : self.number_job,
                                                  'state_appoint' : self.state_appoint,
                                                  'grade_id' : self.grade_id.id,
                                                  'type_appointment' : self.type_appointment.name,
                                                  'degree_id' : self.degree_id.id,
                                                  'date_direct_action': self.date_direct_action 
                                                           })
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تمت الموافقة من قبل '" + unicode(user.name) + u"'")
        
    @api.multi
    def button_refuse_personnel_hr(self):
        self.ensure_one()
        if self.type_appointment.personnel_hr:
            self.state = 'refuse'
        # Add to log
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تم الرفض من قبل شؤون الموظفين)")
        
   
    @api.multi
    def button_accept_direct(self):
        self.ensure_one()
        if self.type_appointment.direct_manager:
            self.state = 'done'
            direct_appoint_obj = self.env['hr.direct.appoint']
            self.env['hr.direct.appoint'].create({'employee_id': self.employee_id.id,
                                                  'number' : self.number,
                                                  'job_id' : self.job_id.id,
                                                  'number_job' : self.number_job,
                                                  'country_id' : self.country_id.id,
                                                  'date_hiring' : self.date_hiring,
                                                  'type_id' : self.type_id.id,
                                                  'state_appoint' : self.state_appoint,
                                                  'grade_id' : self.grade_id.id,
                                                  'type_appointment' : self.type_appointment.name,
                                                  'degree_id' : self.degree_id.id,
                                                  'date_direct_action': self.date_direct_action ,
                                                    })
                                                  
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تمت الموافقة من قبل '" + unicode(user.name) + u"'")
    
    @api.multi
    def button_refuse_direct(self):
        self.ensure_one()
        if self.type_appointment.direct_manager:
            self.state = 'refuse'
        # Add to log
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تم الرفض  من قبل '" + unicode(user.name) + u"'")
        
   
   
    @api.multi
    def action_done(self):
        self.ensure_one()
        for line in self:
            line.employee_id.write({'employee_state':'employee', 'job_id':line.job_id.id})
            line.job_id.write({'state': 'occupied', 'employee': line.employee_id.id, 'occupied_date': fields.Datetime.now()})
        self.state = 'done'
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تمت إحداث تعين جديد '" + unicode(user.name) + u"'")
        # update holidays balance for the employee
       
        
        self.env['hr.holidays']._init_balance(self.employee_id)
        # create promotion history line
        promotion_obj = self.env['hr.employee.promotion.history']
        self.env['hr.employee.promotion.history'].create({'employee_id': self.employee_id.id,
                                                           'salary_grid_id': self.employee_id.job_id.grade_id.id,
                                                           'date_from': self.date_direct_action ,
                                                           'active':True,
                                                           'decision_appoint_id':self.id
                                                           })
    
  


        
#     
              
               
              
    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id.age > 60 :
            raise ValidationError(u"الرجاء التثبت من سن المترشح تجاوز 60)")
        self.number = self.employee_id.number
        self.country_id = self.employee_id.country_id
        appoint_line = self.env['hr.decision.appoint'].search([('employee_id', '=', self.employee_id.id), ('state', '=', 'done'), ('active', '=', True)], limit=1)
        if appoint_line :
            self.emp_job_id = appoint_line.job_id.id
            self.emp_code = appoint_line.job_id.name.number
            self.emp_number_job = appoint_line.number
            self.emp_type_id = appoint_line.type_id.id
            self.emp_far_age = appoint_line.type_id.far_age
            self.emp_grade_id = appoint_line.grade_id.id
            self.emp_department_id = appoint_line.department_id.id
            self.emp_date_direct_action = appoint_line. date_direct_action
               
    @api.onchange('job_id')
    def _onchange_job_id(self):
        if self.job_id :
            self.number_job = self.job_id.number
            self.code = self.job_id.name.number
            self.type_id = self.job_id.type_id.id
            self.far_age = self.job_id.type_id.far_age
            self.grade_id = self.job_id.grade_id.id
            self.department_id = self.job_id.department_id.id
            
            
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
                
    
    @api.onchange('date_direct_action')
    def _onchange_date_direct_action(self):
         if self.date_direct_action :
             if self.date_hiring > self.date_direct_action:
                 raise ValidationError(u"تاريخ مباشرة العمل يجب ان يكون أكبر من تاريخ التعيين")
        
       
    @api.onchange('date_hiring_end')
    def _onchange_date_hiring_end(self):
         if self.date_direct_action :
             if self.date_hiring > self.date_hiring_end:
                 raise ValidationError(u"تاريخ إنتهاء التعيين يجب ان يكون أكبر من تاريخ التعيين")  
                  
class HrTypeAppoint(models.Model):
    _name = 'hr.type.appoint'  
    _description = u'أنواع التعين'
    
    
    name = fields.Char(string='النوع', required=1)
    date_test = fields.Char(string='فترة التجربة') 
    code = fields.Char(string='الرمز')
    
    audit = fields.Boolean(string=u'تدقيق', default=False)
    recrutment_manager = fields.Boolean(string=u'موافقة صاحب صلاحية التعين ', default=True)
    enterview_manager = fields.Boolean(string=u'مقابلة شخصية', default=True)
    personnel_hr = fields.Boolean(string=u'شؤون الموظفين', default=True)
    direct_manager = fields.Boolean(string=u'  موافقة مدير مباشر ', default=True)
    recrutment_decider = fields.Boolean(string=u' موافقة رئيس الهيئة  ', default=True)
    can_be_cancelled = fields.Boolean(string=u'يمكن الغاؤها', default=True)
    
class HrNoticesSettings(models.Model):
    _name = 'hr.notices.settings'  
    _description = u'اشعارات التعين'
    
    
    name = fields.Char(string='المسمى ', required=1)
    description = fields.Char(string='المحتوى') 
    group_notice = fields.Many2many('res.groups', string='إلى') 
    tye_notice_mail = fields.Boolean(string='إشعار عن طريق  بريد إلكتروني ')
    tye_notice_sms = fields.Boolean(string='إشعار عن طريق   إرسال رسالة قصيرة ')
    tye_notice_event = fields.Boolean(string=' عن طريق الإشعار ')
    tyooe_notice = fields.Char(string='طريقة الإشعار')
    

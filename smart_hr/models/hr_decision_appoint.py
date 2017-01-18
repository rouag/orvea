# -*- coding: utf-8 -*-



from openerp import models, fields, api, _
from openerp.exceptions import Warning
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from datetime import date, datetime, timedelta

class HrDecisionAppoint(models.Model):
    _name = 'hr.decision.appoint'  
    _inherit = ['mail.thread'] 
    _description=u'قرار تعيين'
    
    name=fields.Char(string='رقم القرار',required=1 ,states={'new': [('readonly', 0)]})
    order_date=fields.Date(string='تاريخ القرار',required=1) 
    date_hiring=fields.Date(string='تاريخ التعيين',required=1)
    date_hiring_end = fields.Date(string=u'تاريخ إنتهاء التعيين')  
    type_appointment=fields.Many2one('hr.type.appoint',string='نوع التعيين',required=1,states={'new': [('readonly', 0)]})
    date_direct_action=fields.Date(string='تاريخ مباشرة العمل',required=1) 
    instead_exchange=fields.Boolean(string='صرف بدل تعيين')
    active = fields.Boolean( string=u'مفعل', default=True)
    #info about employee
    employee_id=fields.Many2one('hr.employee',string='الموظف',required=1)
    number=fields.Char(string='الرقم الوظيفي',readonly=1) 
    country_id=fields.Many2one(related='employee_id.country_id', store=True, readonly=True, string='الجنسية')
    #info about job
    job_id = fields.Many2one('hr.job', string='الوظيفة',required=1)
    number_job=fields.Char(string='الرقم الوظيفي',readonly=1) 
    
    type_id=fields.Many2one('salary.grid.type',string='الصنف',readonly=1) 
    department_id=fields.Many2one('hr.department',string='القسم',readonly=1)
    grade_id=fields.Many2one('salary.grid.grade',string='المرتبة',readonly=1)
    far_age = fields.Float(string=' السن الاقصى',readonly=1) 
    basic_salary = fields.Float(string='الراتب الأساسي',readonly=1)   
    transport_allow = fields.Float(string='بدل النقل',readonly=1) 
    retirement = fields.Float(string='المحسوم للتقاعد',readonly=1) 
    net_salary = fields.Float(string='صافي الراتب',readonly=1)
    salary_recent = fields.Float(string=' أخر راتب شهري ')
    transport_alocation = fields.Boolean(string='بدل نقل')
    transport_car = fields.Boolean(string='سيارة')
    #other info
    degree_id = fields.Many2one('salary.grid.degree', string='الدرجة', required=1)
    description=fields.Text(string=' ملاحظات ') 
    state = fields.Selection([('new', u'طلب '),
                              ('waiting', u'مقابلة شخصية'),
                              ('budget', u'رئيس الهيئة'),
                              ('hrm', u'شؤون الموظفين'),
                              ('done', u'اعتمدت')
                              ], readonly=1, default='new')
   # state= fields.Selection([('new','طلب'),('waiting','في إنتظار الإعتماد'),('done','اعتمدت')], readonly=1, default='new',) 
    #attachments files
    order_picture=fields.Binary(string='صورة القرار',required=1) 
    medical_examination_file = fields.Binary(string = 'وثيقة الفحص الطبي') 
    order_enquiry_file = fields.Binary(string = 'طلب الاستسفار')
    file_salar_recent = fields.Binary(string = 'تعهد من الموظف')
    file_engagement = fields.Many2many('ir.attachment',string='إرفاق مزيد من الوثائق')
    #file_engagement = fields.Binary(string = 'تعهد من المترشح')
    file_appoint = fields.Binary(string = 'قرار التعين')
    file_decision = fields.Binary(string = 'قرار المباشر')
    
    @api.multi
    def action_waiting(self):
        self.ensure_one()
        self.state = 'waiting'
        if self.employee_id.age > 60 :
            raise ValidationError(u"الرجاء التثبت من سن المترشح تجاوز 60)")
    
    @api.multi
    def action_communication(self):
        self.ensure_one()
        self.state = 'budget'
        # Add to log
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تمت الموافقة من قبل '" + unicode(user.name) + u"' (مديرالهيئة)")

        
    @api.multi
    def action_hrm(self):
        self.ensure_one()
        self.state = 'hrm'
        # Add to log
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تمت الموافقة من قبل شؤون الموظفين)")
    @api.multi
    def action_budget(self):
        self.ensure_one()
        self.state = 'budget'
        # Add to log
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تمت الموافقة من قبل '" + unicode(user.name) + u"'")

   
    @api.multi
    def action_done(self):
        self.ensure_one()
        for line in self:
            line.employee_id.write({'employee_state':'employee','job_id':line.job_id.id})
            line.job_id.write({'state': 'occupied', 'employee': line.employee_id.id, 'occupied_date': fields.Datetime.now()})
          
            
        self.state = 'done'
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تمت إحداث تعين جديد '" + unicode(user.name) + u"'")
        # update holidays balance for the employee
        self.env['hr.holidays']._init_balance(self.employee_id)
        # create promotion history line
        self.env['hr.employee.promotion.history'].create({'employee_id': self.employee_id.id, 'salary_grid_id': self.employee_id.job_id.grade_id.id, 'date_from': fields.Datetime.now() })
    @api.multi
    def action_refuse(self):
        self.ensure_one()
        self.state = 'new'
        # Add to log
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تم رفض تعين جديد من قبل '" + unicode(user.name) + u"'")


        
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
            self.far_age = self.job_id.type_id.far_age
            self.grade_id = self.job_id.grade_id.id
            self.department_id = self.job_id.department_id.id
            
            
    api.onchange('degree_id')
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
    date_test=fields.Char(string='فترة التجربة') 
    code=fields.Char(string='الرمز')
    
    audit = fields.Boolean(string=u'تدقيق', default=False)
    recrutment_manager = fields.Boolean(string=u'صاحب صلاحية التعين', default=True)
    enterview_manager = fields.Boolean(string=u'مقابلة شخصية', default=True)
    personnel_hr = fields.Boolean(string=u'شؤون الموظفين', default=True)
    recrutment_decider = fields.Boolean(string=u'رئيس الهيئة', default=True)
    can_be_cancelled = fields.Boolean(string=u'يمكن الغاؤها', default=True)
    
class HrNoticesSettings(models.Model):
    _name = 'hr.notices.settings'  
    _description=u'اشعارات التعين'
    
    
    name=fields.Char(string='المسمى ',required=1 )
    description=fields.Char(string='المحتوى') 
    group_notice = fields.Many2many('res.groups', string='إلى') 
    tye_notice_mail=fields.Boolean(string='إشعار عن طريق  بريد إلكتروني ')
    tye_notice_sms=fields.Boolean(string='إشعار عن طريق   إرسال رسالة قصيرة ')
    tye_notice_event=fields.Boolean(string=' عن طريق الإشعار ')
    tyooe_notice=fields.Char(string='طريقة الإشعار')
    

# -*- coding: utf-8 -*-


from openerp.exceptions import UserError
from openerp import models, fields, api, _
from openerp.exceptions import Warning
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from datetime import date, datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class HrDecisionAppoint(models.Model):
    _name = 'hr.decision.appoint'
    _order = 'id desc'
    _inherit = ['mail.thread']
    _description = u'قرار تعيين'
    
    name = fields.Char(string='رقم الخطاب', required=1 , states={'draft': [('readonly', 0)]})
    order_date = fields.Date(string='تاريخ الخطاب', required=1) 
    date_hiring = fields.Date(string='تاريخ التعيين', default=fields.Datetime.now(),)
    date_hiring_end = fields.Date(string=u'تاريخ إنتهاء التعيين')  
    date_direct_action = fields.Date(string='تاريخ مباشرة العمل', required=1) 
    instead_exchange = fields.Boolean(string='صرف بدل تعيين')
    is_started = fields.Boolean(string=u'مباشر', default=False)
    # info about employee
    employee_id = fields.Many2one('hr.employee', string='الموظف', required=1)
    number = fields.Char(related='employee_id.number', store=True, readonly=True, string=u'الرقم الوظيفي') 
    emp_code = fields.Char(string=u'رمز الوظيفة ', readonly=1) 
    country_id = fields.Many2one(related='employee_id.country_id', store=True, readonly=True, string='الجنسية')
   
    emp_job_id = fields.Many2one('hr.job', string='الوظيفة', store=True, readonly=1) 
    emp_number_job = fields.Char(string='رقم الوظيفة', store=True, readonly=1) 
    emp_type_id = fields.Many2one('salary.grid.type', string='الصنف', store=True, readonly=1)
    emp_department_id = fields.Many2one('hr.department', string='الادارة', store=True, readonly=1)
    emp_grade_id = fields.Many2one('salary.grid.grade', string='المرتبة', store=True, readonly=1)
    emp_far_age = fields.Float(string=' السن الاقصى', store=True, readonly=1) 
    emp_basic_salary = fields.Float(string='الراتب الأساسي', store=True, readonly=1)   
    emp_degree_id = fields.Many2one('salary.grid.degree', string='الدرجة', store=True, readonly=1)
    # info about job
    job_id = fields.Many2one('hr.job', string='الوظيفة', required=1)
    passing_score = fields.Float(string=u'الدرجة المطلوبه')
    number_job = fields.Char(string='رقم الوظيفة', readonly=1) 
    code = fields.Char(string=u'رمز الوظيفة ', readonly=1) 
    type_id = fields.Many2one('salary.grid.type', string='الصنف', readonly=1) 
    department_id = fields.Many2one('hr.department', string='الادارة', readonly=1)
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة', readonly=1)
    far_age = fields.Float(string=' السن الاقصى', readonly=1) 
    basic_salary = fields.Float(string='الراتب الأساسي', readonly=1)   
    transport_allow = fields.Float(string='بدل النقل', readonly=1) 
    retirement = fields.Float(string='المحسوم للتقاعد', readonly=1) 
    net_salary = fields.Float(string='صافي الراتب', readonly=1)
    salary_recent = fields.Float(string=' أخر راتب شهري ')
    transport_alocation = fields.Boolean(string='بدل نقل')
    transport_car = fields.Boolean(string='سيارة')
    option_contract = fields.Boolean(string='قرار التعاقد')
    degree_id = fields.Many2one('salary.grid.degree', string='الدرجة', required=1)
    # other info
    type_appointment = fields.Many2one('hr.type.appoint', string=u'نوع التعيين' , required=1, advanced_search=True)
    description = fields.Text(string=' ملاحظات ') 
    state_appoint = fields.Selection([
                              ('active', u'مفعل'),
                              ('close', u'مغلق'),
                              ('refuse', u'مرفوض'),
                              ('new', u'في الاجراء'),
                              ], string=u' حالةالتعيين ', default='new', advanced_search=True)
    state = fields.Selection([
                              ('draft', u'طلب'),
                              ('audit', u'تدقيق'),
                              ('waiting', u'مقابلة شخصية'),
                            ('manager', u'صاحب صلاحية التعين'),
                           
                             ('budget', u'رئيس الهيئة'),
                              ('hrm', u'شؤون الموظفين'),
                                ('civil', u'وزارة الخدمة المدنية'),
                                ('direct', u'إدارة الموظف'),
                              ('done', u'اعتمدت'),
                               ('refuse', u'رفض'),
                               ('cancel', u'ملغاة'),
                              ], string=u'حالة', default='draft', advanced_search=True)
    
    
   
    # attachments files
    order_picture = fields.Binary(string='صورة الخطاب', required=1, attachment=True) 
    order_picture_name = fields.Char(string='صورة الخطاب') 
    medical_examination_file = fields.Binary(string='وثيقة الفحص الطبي', attachment=True) 
    date_medical_examination = fields.Date(string='تاريخ الفحص الطبي') 
    medical_examination_name = fields.Char(string='وثيقة الفحص الطبي') 
    order_enquiry_file = fields.Binary(string='طلب الاستسفار', attachment=True)
    file_salar_recent = fields.Binary(string='تعهد من الموظف', attachment=True)
    file_engagement = fields.Many2many('ir.attachment', string='إرفاق مزيد من الوثائق')
    # file_engagement = fields.Binary(string = 'تعهد من المترشح')
    number_appoint = fields.Char(string='رقم قرار التعين ')
    date_appoint = fields.Date(string='تاريخ قرار  التعين')
    file_appoint = fields.Binary(string='صورة قرار التعين', attachment=True)
    
    number_direct_appoint = fields.Char(string='رقم قرار المباشرة ')
    date_direct_appoint = fields.Date(string='تاريخ قرار المباشرة')
    file_direct_appoint = fields.Binary(string='صورة قرار المباشرة', attachment=True)
    file_direct_appoint_name  = fields.Char(string='صورة قرار المباشرة') 
    
    order_enquiry_file_name = fields.Char(string=' طلب الاستسفار') 
    file_salar_recent_name = fields.Char(string=' تعهد من الموظف') 
    file_appoint_name = fields.Char(string='اسم قرار التعين') 
    score = fields.Float(string=u'نتيجة المترشح')
    depend_on_test_periode = fields.Boolean(string=u'مدة التجربة', required=1, readonly=1, states={'draft': [('readonly', 0)]}, default=False)
    testing_date_from = fields.Date(string=u'مدة التجربة (من)')
    testing_date_to = fields.Date(string=u'مدة التجربة (إلى)')

    @api.multi
    @api.onchange('type_appointment')
    def _onchange_type_appointment(self):
        # get list of employee depend on type_appointment
        res = {}
        if self.type_appointment and self.type_appointment.for_members is True:
            employee_ids = self.env['hr.employee'].search([('is_member', '=', True), ('employee_state', 'in', ['done', 'employee'])])
            job_ids = self.env['hr.job'].search([('name.members_job', '=', True)])
            res['domain'] = {'employee_id': [('id', 'in', employee_ids.ids)],'job_id': [('id', 'in', job_ids.ids)]}
            return res
        if self.type_appointment and self.type_appointment.for_members is False:
            employee_ids = self.env['hr.employee'].search([('is_member', '=', False), ('employee_state', 'in', ['done', 'employee'])])
            job_ids = self.env['hr.job'].search([('name.members_job', '=', False)])
            res['domain'] = {'employee_id': [('id', 'in', employee_ids.ids)],'job_id': [('id', 'in', job_ids.ids)]}
            return res

    @api.one
    @api.constrains('score','passing_score')
    def check_score(self):
        self.ensure_one()
        if self.score < self.passing_score:
            raise ValidationError(u"لا يمكن تعين عضو دون الدرجة المطلوبة")

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
        if self.type_appointment.audit and self.type_appointment.enterview_manager:
            self.state = 'waiting'
        if self.type_appointment.audit and self.type_appointment.recrutment_manager:
            self.state = 'manager'
       
        
    @api.multi
    def button_refuse_audit(self):
        self.ensure_one()
        if self.type_appointment.audit:
            self.state = 'draft'
            
            
            
    @api.multi
    def button_accept_civil(self):
        self.ensure_one()
        if self.type_appointment.ministry_civil and self.type_appointment.personnel_hr:
            self.option_contract= True
            self.state = 'hrm'
        
    @api.multi
    def button_refuse_civil(self):
        self.ensure_one()
        if self.type_appointment.ministry_civil:
            self.state = 'manager'
            
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
            if  self.type_appointment.id == self.env.ref('smart_hr.data_hr_recrute_agent_utilisateur') : 
                group_id = self.env.ref('smart_hr.group_personnel_hr')
                self.send_notification_refuse_to_group(group_id)
            if  self.type_appointment.id == self.env.ref('smart_hr.data_hr_recrute_public_retraite')  :
                group_id = self.env.ref('smart_hr.group_personnel_hr')
                self.send_notification_refuse_to_group(group_id)
            self.state = 'refuse'
        
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تم الرفض من قبل '" + unicode(user.name) + u"'")
    @api.multi
    def button_accept_recrutment_decider(self):
        self.ensure_one()
        if self.type_appointment.recrutment_decider and self.type_appointment.personnel_hr:
            self.state = 'hrm'
        if self.type_appointment.recrutment_decider :
            self.action_done()
            self.state_appoint ='active'
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
                                                   'type_appointment' : self.type_appointment.id,
                                                   'degree_id' : self.degree_id.id,
                                                   'date_direct_action': self.date_direct_action 
                                                            })
            
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

        if self.type_appointment.personnel_hr and self.type_appointment.recrutment_decider:
            self.state = 'budget'
        elif self.type_appointment.personnel_hr and self.type_appointment.ministry_civil and self.option_contract == False :
            self.state = 'civil'
        elif self.type_appointment.personnel_hr and self.type_appointment.ministry_civil and self.option_contract == True :
            self.state = 'direct'
        elif self.type_appointment.personnel_hr and self.type_appointment.direct_manager:
            self.state = 'direct'   
        elif self.type_appointment.personnel_hr :
             self.action_done()
             self.state_appoint ='active'
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
                                                   'type_appointment' : self.type_appointment.id,
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
            self.action_done()
            self.state_appoint ='active'
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
                                                  'type_appointment' : self.type_appointment.id,
                                                  'degree_id' : self.degree_id.id,
                                                  'date_direct_action': self.date_direct_action ,
                                                    })
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تمت الموافقة من قبل '" + unicode(user.name) + u"'")

    @api.model
    def control_test_periode_employee(self):
        today_date = fields.Date.from_string(fields.Date.today())
        print"today_date",type(today_date)
        appoints= self.env['hr.decision.appoint'].search([('state','=','done'),('is_started','=',True),('testing_date_to','=', today_date)])
        for line in appoints :
            title= u"' إشعار نهاية مدة التجربة'"
            msg= u"' إشعار نهاية مدة التجربة'"  + unicode(line.employee_id.name) + u"'"
            group_id = self.env.ref('smart_hr.group_department_employee')
            self.send_test_periode_group(group_id,title,msg)
            

            
    def send_test_periode_group(self, group_id, title, msg):
        '''
        @param group_id: res.groups
        '''
        for recipient in group_id.users:
            self.env['base.notification'].create({'title': title,
                                                  'message': msg,
                                                  'user_id': recipient.id,
                                                  'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                  'res_id': self.id,
                                                  'res_action': 'smart_hr.action_hr_decision_appoint',
                                                  'notif': True
                                                  })

             
    @api.model
    def control_prensence_employee(self):
        today_date = fields.Date.from_string(fields.Date.today())
        appoints= self.env['hr.decision.appoint'].search([('state_appoint','=','active'),('state','=','done'),('is_started','=',False)])
        for appoint in appoints :
            direct_appoint_period = appoint.type_appointment.direct_appoint_period
            prev_days_end = fields.Date.from_string(appoint.date_direct_action) + relativedelta(days=direct_appoint_period)
            sign_days = self.env['hr.attendance'].search_count([('employee_id', '=', appoint.employee_id.id), ('name','<=',str(prev_days_end))])
            today_date = str(today_date) 
            prev_days_end = str(prev_days_end)
            if sign_days != 0 or (today_date < prev_days_end) :
                directs= self.env['hr.direct.appoint'].search([('employee_id','=',appoint.employee_id.id),('state','=','waiting')],limit=1)
                print"directs",directs
                if directs:
                    for rec in  directs:
                        rec.write({'state_direct':'confirm' })
                        group_id = self.env.ref('smart_hr.group_personnel_hr')
                        self.send_notification_to_group(group_id)
                
            if sign_days == 0 or (today_date > prev_days_end) :
                directs= self.env['hr.direct.appoint'].search([('employee_id','=',appoint.employee_id.id),('state','=','waiting')],limit=1)
                if directs :
                    for rec in  directs:
                        rec.write({'state_direct':'cancel' })
                        group_id = self.env.ref('smart_hr.group_personnel_hr')
                        self.send_notification_refuse_to_group(group_id)

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
        self.employee_id.write({'employee_state': 'employee','job_id': self.job_id.id,
                                'department_id': self.department_id.id, 'degree_id': self.degree_id.id,
                                  'grade_id':self.grade_id.id})
        if self.date_medical_examination:
            self.employee_id.write({'medical_exam': self.date_medical_examination})
        self.job_id.write({'state': 'occupied', 'employee': self.employee_id.id, 'occupied_date': fields.Datetime.now()})
        self.state = 'done'
        # set salary grid for the employee
        salary_grid_id = self.env['salary.grid.detail'].search([('type_id', '=', self.type_id.id), ('grade_id', '=', self.grade_id.id), ('degree_id', '=', self.degree_id.id)], limit=1)
        if salary_grid_id:
            self.employee_id.write({'salary_grid_id': salary_grid_id.id})
        # close last active appoint for the employee
        last_appoint = self.employee_id.decision_appoint_ids.search([('state_appoint', '=', 'active'), ('is_started', '=', True)], limit=1)
        if last_appoint:
            last_appoint.write({'state_appoint': 'close', 'date_hiring_end': fields.Datetime.now()})
         #send notification to hr personnel
        self.state_appoint ='active'
        user = self.env['res.users'].browse(self._uid)
        self.message_post(u"تمت إحداث تعين جديد '" + unicode(user.name) + u"'")
        # update holidays balance for the employee
        
        type=''
        if self.type_appointment.id == self.env.ref('smart_hr.data_hr_new_agent_public').id:
            type = 'تعيين موظف جديد'
            
        elif self.type_appointment.id == self.env.ref('smart_hr.data_hr_recrute_agent_public').id:
            type = 'تعيين موظف رسمي'
        elif self.type_appointment.id == self.env.ref('smart_hr.data_hr_recrute_agent_utilisateur').id:
            type = 'تعيين الموظفين المستخدمين'
        elif self.type_appointment.id == self.env.ref('smart_hr.data_hr_recrute_salaire_article').id:
            type = 'تعيين عمال بند الأجور'
        elif self.type_appointment.id == self.env.ref('smart_hr.data_hr_recrute_contrat').id:
            type = 'تعيين بعقد'
        elif self.type_appointment.id == self.env.ref('smart_hr.data_hr_recrute_public_nosoudi').id:
            type = 'تعيين غير سعودي على مرتبة رسمية'
        elif self.type_appointment.id == self.env.ref('smart_hr.data_hr_recrute_public_retraite').id:
            type = 'تعيين المحالين على التقاعد'
        if type:
            self.env['hr.employee.history'].sudo().add_action_line(self.employee_id, self.name, self.date_hiring, type)
        self.state = 'done'
        self.env['hr.holidays']._init_balance(self.employee_id)
         # close last active promotion line for the employee
        promotion_obj = self.env['hr.employee.promotion.history']
        previous_promotion = self.env['hr.employee.promotion.history'].search([('employee_id', '=', self.employee_id.id),('active_duration', '=',True)],limit=1)
        if previous_promotion:
            previous_promotion.close_promotion_line()
                   # create promotion history line
        self.env['hr.employee.promotion.history'].create({'employee_id': self.employee_id.id,
                                                           'salary_grid_id': self.employee_id.job_id.grade_id.id,
                                                           'date_from': self.date_direct_action ,
                                                           'active_duration':True,
                                                           'decision_appoint_id':self.id,
                                                           'appoint_type': self.type_appointment.name
                                                           })
       
    def send_notification_refuse_to_group(self, group_id):    
        for recipient in group_id.users:  
            self.env['base.notification'].create({'title': u'إشعار بعدم مباشرة التعين',
                                              'message': u'لقد تم إشعار بعدم مباشرة التعين',
                                              'user_id': recipient.id,
                                              'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                              'res_id': self.id,
                                              'res_action': 'smart_hr.action_hr_decision_appoint',
                                              'notif': True
                                              })



    def send_notification_to_group(self, group_id):
        '''
        @param group_id: res.groups
        '''
        for recipient in group_id.users:
            self.env['base.notification'].create({'title': u' إشعار بمباشرة التعين  ',
                                                  'message': u'لقد تم  المباشرة ',
                                                  'user_id': recipient.id,
                                                  'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                  'res_id': self.id,
                                                  'res_action': 'smart_hr.action_hr_decision_appoint',
                                                  'notif': True
                                                  })







    @api.onchange('employee_id')
    def _onchange_employee_id(self):
       
        self.number = self.employee_id.number
        self.country_id = self.employee_id.country_id
        appoint_line = self.env['hr.decision.appoint'].search([('employee_id', '=', self.employee_id.id), ('state', '=', 'done')], limit=1)
        if appoint_line :
            self.emp_job_id = appoint_line.job_id.id
            self.emp_code = appoint_line.code
            self.emp_number_job = appoint_line.job_id.name.number
            self.emp_type_id = appoint_line.type_id.id
            self.emp_far_age = appoint_line.far_age
            self.emp_grade_id = appoint_line.grade_id.id
            self.emp_degree_id = appoint_line.degree_id.id
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
                 #   self.transport_allow = salary_grid_line.transport_allow
                    self.retirement = salary_grid_line.retirement
                    self.net_salary = salary_grid_line.net_salary


  
    @api.onchange('date_direct_action')
    def _onchange_date_direct_action(self):
         if self.date_direct_action :
             if self.date_hiring > self.date_direct_action:
                 raise ValidationError(u"تاريخ مباشرة العمل يجب ان يكون أكبر من تاريخ التعيين")
 
 
    @api.onchange('date_hiring_end')
    def _onchange_date_hiring_end(self):
         if self.date_hiring_end :
             if self.date_hiring > self.date_hiring_end:
                 raise ValidationError(u"تاريخ إنتهاء التعيين يجب ان يكون أكبر من تاريخ التعيين")  
             
    @api.one
    @api.constrains('order_date')
    def check_order_date(self):
          if self.order_date > datetime.today().strftime('%Y-%m-%d'):
                 raise ValidationError(u"تاريخ الخطاب  يجب ان يكون أصغر من تاريخ اليوم")
    @api.one
    @api.constrains('date_direct_action', 'date_hiring')
    def check_dates_periode(self):
          if self.date_hiring > self.date_direct_action:
                 raise ValidationError(u"تاريخ مباشرة العمل يجب ان يكون أكبر من تاريخ التعيين")

    @api.one
    @api.constrains('date_hiring', 'date_hiring_end')
    def check_dates_end(self):
        if self.date_hiring_end :
            if self.date_hiring > self.date_hiring_end:
                  raise ValidationError(u"تاريخ إنتهاء التعيين يجب ان يكون أكبر من تاريخ التعيين")  

    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft'  :
                raise UserError(_(u'لا يمكن حذف قرار  التعين  إلا في حالة طلب !'))
        return super(HrDecisionAppoint, self).unlink()

class HrTypeAppoint(models.Model):
    _name = 'hr.type.appoint'  
    _description = u'أنواع التعين'

    name = fields.Char(string='النوع', required=1)
    date_test = fields.Char(string='فترة التجربة') 
    code = fields.Char(string='الرمز')
    audit = fields.Boolean(string=u'تدقيق')
    show_in_apoint = fields.Boolean(string=u'إظهار في تعيين', default=True)
    recrutment_manager = fields.Boolean(string=u'موافقة صاحب صلاحية التعين ')
    enterview_manager = fields.Boolean(string=u'مقابلة شخصية')
    personnel_hr = fields.Boolean(string=u'شؤون الموظفين')
    direct_manager = fields.Boolean(string=u'  موافقة إدارة الموظف ')
    recrutment_decider = fields.Boolean(string=u' موافقة رئيس الهيئة  ')
    ministry_civil = fields.Boolean(string=u' موافقة وزارة الخدمة المدنية')
    can_be_cancelled = fields.Boolean(string=u'يمكن الغاؤها')
    for_members = fields.Boolean(string=u'للاعضاء')
    hr_allowance_appoint_id = fields.One2many('hr.allowance.appoint','appoint_type_id', string='البدلات', default=lambda self: self.env.ref('smart_hr.data_allowance_appoint'))
    direct_appoint_period = fields.Float(string=u'فترة مهلة المباشرة')



class HrAllowanceAppoint(models.Model):
    _name = 'hr.allowance.appoint'
    _description = u'بدل التعين'
    hr_allowance_type_id = fields.Many2one('hr.allowance.type', string=u'بدل التعيين')
    salary_number = fields.Float(string=u'عدد الرواتب')
    appoint_type_id = fields.Many2one('hr.type.appoint')

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

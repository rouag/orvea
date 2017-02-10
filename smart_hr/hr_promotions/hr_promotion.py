# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import Warning
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from datetime import date, datetime, timedelta

class hr_promotion(models.Model):
    _name = 'hr.promotion'
    _order = 'id desc'
    _inherit = ['ir.needaction_mixin']
    _description = 'Promotion Decision'

    name = fields.Char(string=u'رقم محضر الترقيات', advanced_search=True)
    date = fields.Date(string=u'تاريخ ', default=fields.Datetime.now())
    speech_number = fields.Char(string=u'رقم الخطاب')
    speech_date = fields.Date(string=u'تاريخ الخطاب')
    speech_file = fields.Binary(string=u'نسخة الخطاب')
    
    decision_number = fields.Char(string=u'رقم قرار الترقية')
    message=fields.Char(string=u'سبب الرفض')
    dicision_date = fields.Date(string=u'تاريخ القرار')
    dicision_file = fields.Binary(string=u'نسخة القرار')
    date_direct_action = fields.Date(string='تاريخ مباشرة العمل',) 
    employee_promotion_line_ids = fields.One2many('hr.promotion.employee', 'promotion_id', string=' قائمة الموظفين',)
    job_promotion_line_ids = fields.One2many('hr.promotion.job', 'promotion_id', string='قائمة الوظائف',)
    employee_job_promotion_line_ids = fields.One2many('hr.promotion.employee.job', 'promotion_id', string=' قائمة الترشيحات',)
 
    state = fields.Selection([
                              ('draft', u'طلب'),
                              ('confirmed', u'مدقق'),
                              ('employee_promotion', u'قائمة مستحقي الترقية'),
                              ('job_promotion', u'الوظائف المحجوزة للترقية'),
                              ('manager', u'صاحب صلاحية التعين'),
                              ('minister', u'وزارة الخدمة المدنية'),
                              ('hrm', u'شؤون الموظفين'),
                              ('done', u'اعتمدت'),
                              ('refuse', u'رفض'),
                              ('cancel', u'ملغاة'),
                              ], string=u'حالة', default='draft', advanced_search=True)
 
    @api.model
    def create(self, vals):
        ret = super(hr_promotion, self).create(vals)
        # Sequence
        vals = {}
        vals['name'] = self.env['ir.sequence'].get('hr.employee.promotion.seq')
        ret.write(vals)
        return ret
    
    
    @api.multi
    def button_confirmed(self):
        for promo in self:
            self.state='confirmed'
            employee_line_list=[]
            for employee_line in self.employee_promotion_line_ids:
                employee_line.state="done"
                
    
    @api.one
    def button_employee_promotion(self):
        self.state='employee_promotion'
    @api.one
    def button_job_promotion(self):
        self.state='job_promotion'
        employee_line_list=[]
        for employee_line in self.employee_promotion_line_ids:
            if not employee_line.emplyoee_state:
                emp_id=self.env['hr.promotion.employee.job'].create({'employee_id':employee_line.employee_id.id,
                                                           'old_job_id': employee_line.old_job_id.id,
                                                           'old_number_job': employee_line.old_number_job ,
                                                           'emp_department_old_id':employee_line.emp_department_old_id.id,
                                                           'emp_grade_id_old':employee_line.emp_grade_id_old.id,
                                                           'promotion_id' : employee_line.promotion_id.id if employee_line.promotion_id else False,
                                                           'point_seniority':employee_line.point_seniority,
                                                           'point_education':employee_line.point_education,
                                                           'point_training':employee_line.point_training,
                                                           'point_functionality':employee_line.point_functionality,
                                                           'sum_point':employee_line.sum_point,}) 
                employee_line_list.append(emp_id.id)
        self.employee_job_promotion_line_ids=employee_line_list
                    
    @api.one
    def button_transfer_manager(self):
        for promo in self:
            self.state='manager'
    
    @api.one
    def button_transfer_minister(self):
        for promo in self:
            self.state='minister'
            
    
    @api.one
    def button_transfer_hrm(self):
        for promo in self:
            self.state='hrm'
    
    @api.one
    def button_done(self):
        for promo in self:
            self.state='done'
            for emp in self.employee_job_promotion_line_ids:
                
                print self.env.ref('smart_hr.data_hr_promotion_agent')
                apoint=self.env["hr.decision.appoint"].create({'name':self.speech_number,
                                                           'order_date': self.speech_date,
                                                           'date_direct_action': self.date_direct_action ,
                                                           'job_id':emp.new_job_id.id,
                                                           'degree_id':emp.emp_grade_id_new.id,
                                                           'type_appointment':self.env.ref('smart_hr.data_hr_promotion_agent').id,
                                                           'order_picture':self.dicision_file,
                                                           'depend_on_test_periode':True,
                                                           'employee_id':emp.employee_id.id,
                                                           'degree_id':emp.new_job_id.grade_id.id,
                                                           })
                apoint.action_done() 
    
    @api.one
    def button_refuse(self):
        for promo in self:
            self.state='draft'
            self.employee_job_promotion_line_ids=[]
            self.job_promotion_line_ids=[]
            
    @api.one
    def button_conceled(self):
        for promo in self:
            self.state='draft'
    
    
    @api.multi
    def create_report_promotion(self):
        self.env['report'].get_pdf(self, 'smart_hr.hr_promotion_report')
           
    @api.model
    def default_get(self,fields):
        res = super(hr_promotion, self).default_get(fields)
        employee_promotion=[]
        employee_promotion_job=[]
        employees=self.env['hr.employee'].search([])
        for emp in employees:
            if emp.job_id.grade_id: 
                suspend =  self.env['hr.suspension'].search([('employee_id', '=', emp.id), ('suspension_date', '<', date.today()),('suspension_end_id.release_date', '>', date.today())])
                holidays_status_exceptiona=self.env['hr.holidays'].search([('employee_id', '=', emp.id),('date_from', '<', date.today()),('date_to', '<', date.today()),('holiday_status_id.id','=',self.env.ref('smart_hr.data_hr_holiday_status_exceptional').id)])
                holidays_status_study=self.env['hr.holidays'].search([('employee_id', '=', emp.id),('date_from', '<', date.today()),('date_to', '<', date.today()),('holiday_status_id.id','=',self.env.ref('smart_hr.data_hr_holiday_status_study').id),('duration','>',180)])
                sanctions=self.env['hr.sanction'].search([('state','=','done'),('date_sanction_start','>',datetime.now()+relativedelta(years=-1))])
                saanction_days=True
                if not suspend and not holidays_status_exceptiona and not holidays_status_study:
                    if  emp.promotion_duration/365 >  emp.job_id.grade_id.years_job  :
                        days=0
                        print  emp.promotion_duration
                        if  emp.sanction_ids:
                            for sanction in sanctions:
                                if sanction.state=="done" and  not sanction.type_sanction.code == "4" :
                                    for line in sanction.line_ids:
                                        if line.state=='done':
                                            if line.employee_id.id==emp.id:
                                                days=days + line.nb_days_old
                                    if sanction.type_sanction.code == "4":
                                         saanction_days=False
                            if  days <  15  and saanction_days: 
                                        employee_promotion.append(emp)
                        else:
                            employee_promotion.append(emp)
        for emp_promotion in employee_promotion :
            print emp_promotion
            regle_point=self.env['hr.evaluation.point'].search([('grade_id','=',emp_promotion.job_id.grade_id.id)])
            demande_promotion_id=self.env['hr.promotion.employee.demande'].search([('employee_id','=',emp_promotion.id)])
            point_seniority=0
            education_point=0
            trining_point=0
            point_functionality=0
            years_supp=(emp_promotion.service_duration/365)-emp_promotion.job_id.grade_id.years_job
            if years_supp > 0 :
                
                for year in   xrange(1, years_supp):
                    for seniority in regle_point.seniority_ids :
                        if  (year >= seniority.year_from )and (year <= seniority.year_to) :
                            point_seniority= point_seniority + (seniority.point)
            try:    
                education_level_job= emp_promotion.job_id.serie_id.hr_classment_job_ids[0].level_education_id.nomber_year_education 
            except:
                education_level_job=False
            if education_level_job:
                for education_level_emp in emp_promotion.education_level_ids:
                    if education_level_emp.level_education_id.nomber_year_education - education_level_job >0:
                        if education_level_emp.job_specialite:
                            if education_level_emp.level_education_id.secondary:
                                for education in regle_point.education_ids :
                                    if education.nature_education=='after_secondry' and   education.type_education=="in_speciality_job":
                                        education_point = education_point + (education.year_point* (education_level_emp.nomber_year_education - education_level_job))
                            else:   
                                for education in regle_point.education_ids :
                                    if education.nature_education=='before_secondry' and   education.type_education=="in_speciality_job":
                                        education_point = education_point + (education.year_point* (education_level_emp.nomber_year_education - education_level_job))  
                               
                        else:
                            if education_level_emp.level_education_id.secondary:
                                for education in regle_point.education_ids :
                                    if education.nature_education=='after_secondry' and   education.type_education=="not_speciality_job":
                                        education_point = education_point + (education.year_point* (education_level_emp.nomber_year_education - education_level_job))
                                            
                            else:   
                                for education in regle_point.education_ids :
                                    if education.nature_education=='before_secondry' and   education.type_education=="not_speciality_job":
                                        education_point = education_point + (education.year_point* (education_level_emp.nomber_year_education - education_level_job))  
                
            
            
            trainings=self.env['hr.candidates'].search([('employee_id','=',emp_promotion.id),('state','=','done')])
            for training in trainings:
                if training.number_of_days>12 and training.experience=='experience_directe':
                    for trainig in regle_point.training_ids :
                        if trainig.type_training=='direct_experience':
                            trining_point=trining_point + trainig.point
                elif training.number_of_days>12 and training.experience=='experience_in_directe':
                    for trainig in regle_point.training_ids :
                        if trainig.type_training=='indirect_experience':
                            trining_point=trining_point + trainig.point
                
            id_emp= self.env['hr.promotion.employee'].create({'employee_id': emp_promotion.id,
                                                           'old_job_id': emp_promotion.job_id.id,
                                                           'old_number_job': emp_promotion.job_id.number ,
                                                           'emp_department_old_id':emp_promotion.department_id.id,
                                                           'emp_grade_id_old':emp_promotion.job_id.grade_id.id,
                                                           'promotion_id':demande_promotion_id[0].id if demande_promotion_id else False,
                                                           'point_seniority':point_seniority,
                                                           'point_education':education_point,
                                                           'point_training':trining_point,
                                                           'point_functionality':point_functionality,
                                                           'sum_point':education_point+trining_point+point_seniority+point_functionality,
                                                           
                                                           }) 
         
            employee_promotion_job.append(id_emp.id)
        res['employee_promotion_line_ids'] = [(6, 0, employee_promotion_job)]
        if not employee_promotion_job :
            raise ValidationError(u"لا يوجد موظفون مؤهلون للترقية")
        job_promotion=[]
        for job in self.env['hr.job'].search([('state','=','unoccupied')]) :
            id_job= self.env['hr.promotion.job'].create({'new_job_id': job.id,
                                                              'emp_grade_id_new':job.grade_id.id,
                                                              'new_number_job':job.number,
                                                        
                                                           }) 
            job_promotion.append(id_job.id)
        res['job_promotion_line_ids'] = [(6, 0, job_promotion)]
        if not employee_promotion_job :
            raise ValidationError(u"لا توجد وظائف شاغرة")
        
       
        return res
    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft' and self._uid != SUPERUSER_ID:
                raise ValidationError(u'لا يمكن حذف قرار الترقية في هذه المرحلة يرجى مراجعة مدير النظام')
        return super(hr_promotion, self).unlink()
    
    



    
class hr_promotion_ligne_employee(models.Model):
    _name = 'hr.promotion.employee'
    _order = 'id desc'
    employee_id = fields.Many2one('hr.employee', string=u'الموظف')
    promotion_id = fields.Many2one('hr.promotion', string=u'الترقية ')
    demande_promotion_id = fields.Many2one('hr.promotion.employee.demande', string=u'طلب الترقية  ')
    old_job_id = fields.Many2one('hr.job', string=u'الوظيفة الحالية')
    old_number_job = fields.Char(string='رقم الوظيفة', store=True, readonly=1) 
    emp_department_old_id = fields.Many2one('hr.department', string='الادارة', store=True, readonly=1)
    emp_grade_id_old = fields.Many2one('salary.grid.grade', string='المرتبةالحالية ', store=True, readonly=1)
    point_seniority=fields.Integer(string=u'نقاط الأقدمية',)
    point_education=fields.Integer(string=u'نقاط التعليم',)
    point_training=fields.Integer(string=u'نقاط التدريب',)
    point_functionality=fields.Integer(string=u'نقاط  الإداء الوظيفي',)
    sum_point=fields.Integer(string=u'المجموع',)
    emplyoee_state = fields.Boolean(string='تأجيل',)
    state = fields.Selection([('draft', u'طلب'),
                              ('done', u'اعتمدت'),
                              ], string=u'حالة', default='draft', advanced_search=True)
    
    @api.multi
    def employee_pause(self):
        self.emplyoee_state=True


    

class hr_promotion_ligne_jobs(models.Model):
    _name = 'hr.promotion.job'
    _order = 'id desc'
    
    new_job_id = fields.Many2one('hr.job', string=u'الوظيفة المرقى عليها',domain=[('state','=','unoccupied')])
    new_number_job = fields.Char(string='رقم الوظيفة', store=True, readonly=1)
    promotion_id = fields.Many2one('hr.promotion', string=u'الترقية ')
    department = fields.Many2one('hr.department', string='الادارة', store=True, readonly=1)
    emp_grade_id_new = fields.Many2one('salary.grid.grade', string='المرتبة ', store=True, readonly=1,)
    job_state = fields.Boolean(string='حجز',)
    
    
     
    @api.onchange('new_job_id')
    def onchange_job_id(self):
        if self.new_job_id:
            self.emp_grade_id_new = self.new_job_id.grade_id.id
            self.new_number_job = self.new_job_id.number
    
    @api.multi
    def job_reserved(self):
        if self.new_job_id:
            self.job_state=True
    @api.multi
    def job_in_reserved(self):
        if self.new_job_id:
            self.job_state=False
    
            
class hr_promotion_ligne_employee_job(models.Model):
    _name = 'hr.promotion.employee.job'
    _order = 'id desc'
    
    employee_id = fields.Many2one('hr.employee', string=u'الموظف')
    job_promotion_id = fields.Many2one('hr.promotion.job', string=u'الوظيفة المرقى عليها',)
    promotion_id = fields.Many2one('hr.promotion', string=u'الترقية ')
    old_job_id = fields.Many2one('hr.job', string=u'الوظيفة الحالية')
    old_number_job = fields.Char(string='رقم الوظيفة', store=True, readonly=1) 
    emp_department_old_id = fields.Many2one('hr.department', string='الادارة', store=True, readonly=1)
    emp_grade_id_old = fields.Many2one('salary.grid.grade', string='المرتبةالحالية ', store=True, readonly=1)
    point_seniority=fields.Integer(string=u'نقاط الأقدمية',)
    point_education=fields.Integer(string=u'نقاط التعليم',)
    point_training=fields.Integer(string=u'نقاط التدريب',)
    point_functionality=fields.Integer(string=u'نقاط  الإداء الوظيفي',)
    sum_point=fields.Integer(string=u'المجموع',)
    demande_promotion_id = fields.Many2one('hr.promotion.employee.demande', string=u'طلب الترقية  ')
    new_job_id = fields.Many2one('hr.job', string=u'الوظيفة المرقى عليها',domain=[('state','=','unoccupied')])
    new_number_job = fields.Char(string='رقم الوظيفة', store=True, readonly=1)
    department = fields.Many2one('hr.department', string='الادارة', store=True, readonly=1)
    emp_grade_id_new = fields.Many2one('salary.grid.grade', string='المرتبة ', store=True, readonly=1,)
    promotion_supp = fields.Boolean(string='علاوة إضافية',)
    state = fields.Selection([('draft', u'طلب'),
                              ('refuse', u'رفض'),
                              ('done', u'اعتمدت'),
                              ], string=u'حالة', default='draft', advanced_search=True)
    

    @api.multi
    def promotion_confirmed(self):
        if self.new_job_id:
            self.new_job_id.state='occupied'
            self.state="done"
    
   
    @api.multi
    def job_refuse(self):
        if self.new_job_id:
            self.new_job_id.state='unoccupied'
            self.state="refuse"
            
    @api.onchange('new_job_id')
    def onchange_job_id(self):
        if self.new_job_id:
            self.emp_grade_id_new = self.new_job_id.grade_id.id
            self.new_number_job = self.new_job_id.number
  
class hr_promotion_type(models.Model):
    _name = 'hr.promotion.type'
     
    name = fields.Char(string=u'نوع الترقية', advanced_search=True)
    code = fields.Char(string=u'الرمز')
    hr_allowance_type_id = fields.Many2one('hr.allowance.type', string='أنواع البدلات',)
    percent_salaire = fields.Float(string=u' علاوة إضافية نسبة من الراتب  ',)
   
class hr_promotion_demande(models.Model):
    _name = 'hr.promotion.employee.demande'
    _order = 'id desc'
    
    create_date = fields.Datetime(string=u'تاريخ الطلب', default=fields.Datetime.now())
    employee_id = fields.Many2one('hr.employee', string='صاحب الطلب', default=lambda self: self.env['hr.employee'].search([('user_id', '=', self._uid)], limit=1), required=1, readonly=1)
    name = fields.Char(string=u'رقم الطلب', advanced_search=True)
    description1 = fields.Text(string='رغبات الموظف', ) 
    description2 = fields.Text(string='رغبات الموظف', ) 
    description3 = fields.Text(string='رغبات الموظف', ) 
    description4 = fields.Text(string='رغبات الموظف', ) 
    description5 = fields.Text(string='رغبات الموظف', ) 
    city_fovorite = fields.Many2one('res.city', string=u'المدينة المفضلة')
    hr_allowance_type_id = fields.Many2one('hr.allowance.type', string='أنواع البدلات(بدل طبيعة عمل )',)
    old_job_id=fields.Many2one(related='employee_id.job_id', store=True, readonly=True,string=u'الوظيفة الحالية',)
    department_id=fields.Many2one(related='employee_id.department_id', store=True, readonly=True,string='الادارة',)
    
    @api.model
    def create(self, vals):
        ret = super(hr_promotion_demande, self).create(vals)
        # Sequence
        vals = {}
        vals['name'] = self.env['ir.sequence'].get('hr.employee.demande.promotion.seq')
        ret.write(vals)
        return ret


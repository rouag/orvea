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
    letter_sender = fields.Char(string=u'جهة الخطاب', advanced_search=True)
    letter_number = fields.Char(string=u'رقم الخطاب', advanced_search=True)
    letter_date = fields.Date(string=u'تاريخ الخطاب')
    employee_promotion_line_ids = fields.One2many('hr.promotion.employee', 'promotion_id', string=' قائمة الموظفين',)

 
    state = fields.Selection([
                              ('draft', u'طلب'),
                              ('confirmed', u'مدقق'),
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
    
    
    @api.one
    def button_confirmed(self):
        for promo in self:
            self.state='confirmed'
            for promo in promo.employee_promotion_line_ids :
                promo.etape='confirmed'
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
    
    @api.one
    def button_refused(self):
        for promo in self:
            self.state='refuse'
            
    @api.one
    def button_conceled(self):
        for promo in self:
            self.state='cancel'
           
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
                if not suspend and not holidays_status_exceptiona and not holidays_status_study:
                    if  emp.promotion_duration/365 >  emp.job_id.grade_id.years_job  :
                        days=0
                        print  emp.promotion_duration
                        if  emp.sanction_ids:
                            for sanction in sanctions:
                                for line in sanction.line_ids:
                                    print 'line.employee_id',line.employee_id
                                    if line.employee_id.id==emp.id:
                                        days=days + sanction.nb_days
                                if  days <  15  and  not sanction.type_sanction.code == "4" :
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
            print "111",emp_promotion.job_id.serie_id
            print "2222" ,emp_promotion.job_id.name
            print "2222" ,emp_promotion.job_id.id
            education_level_job= emp_promotion.job_id.serie_id.hr_classment_job_ids[0].education_level_id.nomber_year_education
            for education_level_emp in emp_promotion.education_level_ids:
                if education_level_emp.nomber_year_education - education_level_job >0:
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
            
            
            for evaluation in emp_promotion.evaluation_level_ids:
                point_functionality=0
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
                
              
            list_job=[]
            grade_id_employee=emp_promotion.job_id.grade_id.code
            try:
                grade_id_employee = int(grade_id_employee)
            except ValueError: 
                print 'error'
            print 'grade_id_employee',grade_id_employee
            for job in self.env['hr.job'].search([('state','=','unoccupied')]):
                if int(job.grade_id.code) == (grade_id_employee+1):
                    print int(job.grade_id.code)
                    list_job.append(job.id)
            print 'list',list_job
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
                                                           'etape': 'draft',
                                                           
                                                           }) 
            employee_promotion_job.append(id_emp.id)
        res['employee_promotion_line_ids'] = [(6, 0, employee_promotion_job)]
        res.update(domain={
        'new_job_id': ['id', 'in',list_job ]
    })
        return res
    
    
   
    
    
    @api.multi
    def unlink(self):
        for rec in self:
            if rec.state != 'draft' and self._uid != SUPERUSER_ID:
                raise ValidationError(u'لا يمكن حذف قرار الترقية في هذه المرحلة يرجى مراجعة مدير النظام')
        return super(hr_promotion, self).unlink()
    
    


class hr_promotion_type(models.Model):
    _name = 'hr.promotion.type'
     
    name = fields.Char(string=u'نوع الترقية', advanced_search=True)
    code = fields.Char(string=u'الرمز')
    
class hr_promotion_ligne(models.Model):
    _name = 'hr.promotion.employee'
    _order = 'id desc'
    employee_id = fields.Many2one('hr.employee', string=u'الموظف')
    promotion_id = fields.Many2one('hr.promotion', string=u'الترقية ')
    demande_promotion_id = fields.Many2one('hr.promotion.employee.demande', string=u'طلب الترقية  ')
    old_job_id = fields.Many2one('hr.job', string=u'الوظيفة الحالية')
    new_job_id = fields.Many2one('hr.job', string=u'الوظيفة المرقى عليها',)
    old_number_job = fields.Char(string='رقم الوظيفة', store=True, readonly=1) 
    new_number_job = fields.Char(string='رقم الوظيفة', store=True, readonly=1) 
    emp_department_old_id = fields.Many2one('hr.department', string='الادارة', store=True, readonly=1)
    emp_grade_id_old = fields.Many2one('salary.grid.grade', string='المرتبةالحالية ', store=True, readonly=1)
    emp_grade_id_new = fields.Many2one('salary.grid.grade', string='المرتبة الجديدة', store=True, readonly=1,domain=[('state','=','unoccupied'),])
    point_seniority=fields.Integer(string=u'نقاط الأقدمية',)
    point_education=fields.Integer(string=u'نقاط التعليم',)
    point_training=fields.Integer(string=u'نقاط التدريب',)
    point_functionality=fields.Integer(string=u'نقاط  الإداء الوظيفي',)
    sum_point=fields.Integer(string=u'المجموع',)
    etape = fields.Selection([
                              ('draft', u'طلب'),
                              ('confirmed', u'مدقق'),
                              ('reserved', u'محجوزة'),
                              ('done', u'اعتمدت'),
                              ('refuse', u'رفض'),
                              ('cancel', u'ملغاة'),
                              ], string=u'حالة', default='draft', advanced_search=True)
    state = fields.Selection([
                              ('draft', u'طلب'),
                              ('confirmed', u'مدقق'),
                              ('reserved', u'محجوزة'),
                              ('done', u'اعتمدت'),
                              ('refuse', u'رفض'),
                              ('cancel', u'ملغاة'),
                              ], string=u'حالة', default='draft', advanced_search=True)
    
    
    @api.onchange('new_job_id')
    def onchange_job_id(self):
        if self.new_job_id:
            self.emp_grade_id_new = self.new_job_id.grade_id.id
            self.new_number_job = self.new_job_id.number
            
    @api.multi
    def job_reserved(self):
        if self.new_job_id:
            self.new_job_id.state='reserved'
            self.etape="reserved"
    
    @api.multi
    def job_confirmed(self):
        if self.new_job_id:
            self.new_job_id.state='occupied'
            self.etape="done"
           
            
    @api.multi
    def job_refused(self):
        if self.new_job_id:
            self.new_job_id.state='unoccupied'
            self.etape="refuse"
            

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



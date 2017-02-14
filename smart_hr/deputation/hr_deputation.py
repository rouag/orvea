# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import Warning
from openerp.exceptions import ValidationError
from openerp.exceptions import UserError
from datetime import date, datetime, timedelta
from dateutil.relativedelta import relativedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT
from umalqurra.hijri_date import HijriDate

class HrDeputation(models.Model):
    _name = 'hr.deputation'
    _order = 'id desc'
    _rec_name = 'order_date'
    _description = u'الانتدابات'

    order_date = fields.Date(string='تاريخ الطلب', default=fields.Datetime.now(), readonly=1)
    employee_id = fields.Many2one('hr.employee', string=' إسم الموظف', required=1)
    number = fields.Char(string='الرقم الوظيفي', readonly=1)
    code = fields.Char(string=u'رمز الوظيفة ', readonly=1)
    country_id = fields.Many2one(related='employee_id.country_id', store=True, readonly=True, string='الجنسية')
  
    number_job = fields.Char(string='رقم الوظيفة', store=True, readonly=1)
    job_id = fields.Many2one('hr.job', string='الوظيفة', store=True, readonly=1)
    type_id = fields.Many2one('salary.grid.type', string='الصنف', store=True, readonly=1)
    department_id = fields.Many2one('hr.department', string='الادارة', store=True, readonly=1)
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة', store=True, readonly=1)
    degree_id = fields.Many2one('salary.grid.degree', string='الدرجة', store=True, readonly=1)
    date_from = fields.Date(string=u'من')
    date_to = fields.Date(string=u'الى')
    date_start = fields.Date(string=u'من')
    date_end = fields.Date(string=u'الى')
    note = fields.Text(string=u'الملاحظات', readonly=1, states={'draft': [('readonly', 0)]})
    decision_number = fields.Char(string='رقم القرار')
    decision_date = fields.Date(string='تاريخ القرار', default=fields.Datetime.now(), readonly=1)
    file_decision = fields.Binary(string='نسخة من الحالة الميزانية')
    file_decision_name = fields.Char(string='نسخة من الحالة الميزانية')
    
    lettre_number = fields.Char(string='رقم خطاب التغطية')
    lettre_date = fields.Date(string='تاريخ خطاب التغطية', default=fields.Datetime.now(), readonly=1)
    file_lettre = fields.Binary(string='نسخة خطاب التغطية')
    file_lettre_name = fields.Char(string='نسخة خطاب التغطية')
    
    report_number = fields.Char(string='عنوان التقرير')
    report_date = fields.Date(string='تاريخ التقرير', default=fields.Datetime.now(), readonly=1)
    file_report = fields.Binary(string='صورة التقرير')
    file_report_name = fields.Char(string='صورة التقرير')
   
    amount = fields.Float(string='المبلغ')
    file_order = fields.Binary(string='صورة القرار ')
    transport_alocation = fields.Boolean(string='بدل نقل')
    net_salary = fields.Boolean(string=' الراتب')
    anual_balance = fields.Boolean(string=' الرصيد السنوي')
    alowance_bonus = fields.Boolean(string=' البدلات و التعويضات و المكافات')
    the_availability = fields.Selection([
        ('hosing_and_food', u'السكن و الطعام '),
        ('hosing_or_food', u'السكن أو الطعام '),
         ('nothing', u'لا شي '),
         ], string=u'الجهة توفر', default='hosing_and_food')
    type = fields.Selection([
        ('internal', u'داخلى'),
        ('external', u'خارجى')], string=u'نوع الإنتداب', default='internal')
    city_id = fields.Many2one('res.city', string=u'المدينة')
    category_id = fields.Many2one('hr.deputation.category', string=u'فئة التصنيف')
    state = fields.Selection([
                              ('draft', u'طلب'),
                              ('audit', u'دراسة الطلب'),
                              ('waiting', u'اللجنة'),
                              ('done', u'اعتمدت'),
                              ('order', u'إصدار التقرير'),
                              ('humain', u'موارد البشرية'),
                              ('finish', u'منتهية'),
                               ('refuse', u'مرفوض')
                              ], string=u'حالة', default='draft', advanced_search=True)
    task_name = fields.Many2one('hr.employee.task',string=u' المهمة')
    duration = fields.Integer(string=u'المدة', compute='_compute_duration')


    @api.onchange('task_name')
    def _onchange_task_name(self):
        if self.task_name :
            self.date_from = self.task_name.date_from
            self.date_to = self.task_name.date_to
#             self.employee_id = self.task_name.employee_id.id
#             self.number = self.task_name.employee_id.number
#             self.country_id = self.task_name.employee_id.country_id.id
#             self.department_id = self.task_name.employee_id.department_id.id
#             self.job_id = self.task_name.employee_id.job_id.id
#             self.type_id = self.task_name.employee_id.type_id.id




    @api.multi
    def action_draft(self):
        for deputation in self:
            deputation.state = 'audit'
         
    @api.multi
    def action_commission(self):
        for deputation in self:
            deputation.state = 'waiting'   
   
    @api.multi
    def action_audit(self):
        for deputation in self:
            deputation.state = 'done'   
    @api.multi
    def action_waiting(self):
        for deputation in self:
            deputation.state = 'done'

    @api.multi
    def action_done(self):
        for deputation in self:
            deputation.state = 'order'
    
    @api.multi
    def action_order(self):
        for deputation in self:
            deputation.state = 'humain'

    @api.multi
    def action_humain(self):
        for deputation in self:
            deputation.state = 'finish'
            
    @api.multi
    def action_refuse(self):
        for deputation in self:
            deputation.state = 'refuse'
            
    @api.one
    @api.depends('date_from', 'date_to')
    def _compute_duration(self):
        if self.date_from and self.date_to:
            date_from = fields.Date.from_string(self.date_from)
            date_to = fields.Date.from_string(self.date_to)
            self.duration = (date_to - date_from).days + 1
    

   
            
    @api.onchange('employee_id')
    def _onchange_employee_id(self):
        if self.employee_id :
            self.number = self.employee_id.number
            self.country_id = self.employee_id.country_id
            appoint_line = self.env['hr.decision.appoint'].search([('employee_id', '=', self.employee_id.id), ('state', '=', 'done')], limit=1)
            if appoint_line :
                self.job_id = appoint_line.job_id.id
                self.code = appoint_line.job_id.name.number
                self.number_job = appoint_line.number
                self.type_id = appoint_line.type_id.id
                self.grade_id = appoint_line.grade_id.id
                self.department_id = appoint_line.department_id.id
                
                
                
    @api.one
    @api.constrains('date_from', 'date_to')
    def check_dates_periode(self):
        # Objects
        holiday_obj = self.env['hr.holidays']
        candidate_obj = self.env['hr.candidates']
        deput_obj = self.env['hr.deputation']
         
            # Date validation

        if self.date_from > self.date_to:
            raise ValidationError(u"تاريخ من يجب ان يكون أصغر من تاريخ الى")
            # check minimum request validation
       
            # التدريب
        search_domain = [
                ('employee_id', '=', self.employee_id.id),
                ('state', '=', 'done'),
            ]
 
        for rec in candidate_obj.search(search_domain):
            dateto = fields.Date.from_string(rec.date_to)
            datefrom = fields.Date.from_string(rec.date_from)
            res = relativedelta(dateto, datefrom)
            months = res.months
            days = res.days
                # for none normal holidays test
        for rec in holiday_obj.search(search_domain):
            if rec.date_from <= self.date_from <= rec.date_to or \
                rec.date_from <= self.date_to <= rec.date_to or \
                self.date_from <= rec.date_from <= self.date_to or \
                self.date_from <= rec.date_to <= self.date_to:
                raise ValidationError(u"هناك تداخل في التواريخ مع قرار سابق في الإجازة")
 
        
            # الإنتداب
        search_domain = [
                ('employee_id', '=', self.employee_id.id),
                ('state', '=', 'done'),
            ]
        for rec in deput_obj.search(search_domain):
            if rec.date_from <= self.date_from <= rec.date_to or \
                    rec.date_from <= self.date_to <= rec.date_to or \
                    self.date_from <= rec.date_from <= self.date_to or \
                    self.date_from <= rec.date_to <= self.date_to:
                raise ValidationError(u"هناك تداخل في التواريخ مع قرار سابق في الإنتداب")
 
    
class HrDeputationCategory(models.Model):
    _name = 'hr.deputation.category'

    category = fields.Selection([
        ('high', u'مرتفعة'),
        ('a', u'أ'),
        ('b', u'ب'),
        ('c', u'ج'),
    ], string=u'الفئات', default='c')
    country_ids = fields.Many2many('res.country', 'category_deputation_country_rel', 'country_id', 'category_id', string=u'البلاد')

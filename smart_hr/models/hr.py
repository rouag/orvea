# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from openerp.exceptions import Warning
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from datetime import date
from datetime import date, datetime, timedelta


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    def _compute_loans_count(self):
        for rec in self:
            rec.loan_count = self.env['hr.loan'].search_count([('employee_id', '=', rec.id)])

    number = fields.Char(string=u'الرقم الوظيفي', required=1)
    identification_date = fields.Date(string=u'تاريخ إصدار بطاقة الهوية ')
    identification_place = fields.Many2one('res.city', string=u'مكان إصدار بطاقة الهوية')
    father_name = fields.Char(string=u'إسم الأب', required=1)
    is_resident = fields.Boolean(string=u'موظف مقيم', required=1)
    birthday_location = fields.Char(string=u'مكان الميلاد')
    attachments = fields.Many2many('ir.attachment', 'res_id', string=u"المرفقات")
    recruiter = fields.Many2one('recruiter.recruiter', string=u'جهة التوظيف', required=1)
    recruiter_date = fields.Date(string=u' تاريخ التعين بالجهة ', required=1)
    employee_state = fields.Selection([('new', u'جديد'),
                                       ('waiting', u'في إنتظار الموافقة'),
                                       ('update', u'إستكمال البيانات'),
                                       ('done', u'اعتمدت'),
                                       ('refused', u'رفض'),
                                      ( 'outside_assignment',u'مكلف خارجي'),
                                      ('non_active',u'مفصول'),
                                      ('oh',u'كف اليد'),
                                      ('retired',u'متقاعد'),
                                      ('employee', u'موظف')], string=u'الحالة', default='new')
    education_level = fields.Many2one('hr.employee.education.level', string=u'المستوى التعليمي')
    # Deputation Stock
    deputation_stock = fields.Integer(string=u'الأنتدابات', default=60)
    service_duration = fields.Integer(string=u'مدة الخدمة(يوم)', readonly=True)
    religion_state = fields.Many2one('religion.religion',string=u'الديانة', required=1)
    emp_state = fields.Selection([('working', u'على رأس العمل'),
                                  ('suspended', u'مكفوف اليد'),
                                  ('terminated', u'مطوي قيده'),
                                  ], string=u'الحالة', default='working', advanced_search=True)
    decision_appoint_ids = fields.One2many('hr.decision.appoint', 'employee_id', string=u'تعيينات الموظف')
    job_id = fields.Many2one('hr.job', advanced_search=True)
    age = fields.Integer(string=u'السن', compute='_compute_age')
    employee_no = fields.Integer(string=u'رقم الموظف', advanced_search=True)
    join_date = fields.Date(string=u'تاريخ الالتحاق بالجهة')
    external_decision = fields.Boolean(string=u'موافقة خارجية', default=False)
    holidays = fields.One2many('hr.holidays', 'employee_id', string=u'الاجازات')
    holidays_balance = fields.One2many('hr.employee.holidays.stock', 'employee_id', string=u'الأرصدة', readonly=1)
    promotions_history = fields.One2many('hr.employee.promotion.history', 'employee_id', string=u'الترقيات')
    traveling_ticket = fields.Boolean(string=u'تذكرة سفر', default=False)
    traveling_family_ticket = fields.Boolean(string=u'تذكرة سفر عائليّة', default=False)
    compensation_stock = fields.Integer(string=u'رصيد إجازات التعويض')
    holiday_peiodes = fields.One2many('hr.holidays.periode', 'employee_id', string='holidays periodes')
    grandfather_name = fields.Char(string=u'اسم الجد', required=1)
    grandfather2_name = fields.Char(string=u'  اسم الجد الثاني ')
    family_name = fields.Char(string=u'الاسم العائلي', required=1)
    father_middle_name = fields.Char(string=u'middle_name')
    grandfather_middle_name = fields.Char(string=u'middle_name2')
    grandfather2_middle_name = fields.Char(string=u'  middle_name3')
    space = fields.Char(string=' ', default=" ", readonly=True)
    begin_work_date = fields.Date(string=u' تاريخ بداية العمل الحكومي', required=1)
    promotion_duration = fields.Integer(string=u'مدة الترقية(يوم)', compute='_compute_promotion_days')
    dep_city = fields.Many2one('res.city', strin=u'المدينة', related="department_id.dep_city")
    dep_Side = fields.Many2one('city.side', string=u'الجهة', related="department_id.dep_Side")
    history_ids = fields.One2many('hr.employee.history', 'employee_id', string=u'سجل الاجراءات')
    diploma_id = fields.Many2one('hr.employee.diploma', string=u'الشهادة')
    specialization_ids = fields.Many2many('hr.employee.specialization', string=u'الاختصاص')
    passport_date = fields.Date(string=u'تاريخ إصدار جواز السفر ')
    passport_place = fields.Char(string=u'مكان إصدار جواز السفر')
    passport_end_date = fields.Date(string=u'تاريخ انتهاء جواز السفر ')
    display_name = fields.Char(compute='_compute_display_name', string='display Name', select=True)
    sanction_ids = fields.One2many('hr.employee.sanction', 'employee_id', string=u'العقوبات')
    bank_account_ids = fields.One2many('res.partner.bank','employee_id', string=u'الحسابات البنكِيّة')
    loan_count = fields.Integer(string=u'عدد القروض', compute='_compute_loans_count')
   
    @api.one
    @api.depends('name', 'father_middle_name', 'father_name', 'family_name')
    def _compute_display_name(self):
        display_name = self.name
        if self.father_name:
            if self.father_middle_name:
                display_name += ' '+self.father_middle_name +' '+ self.father_name
            else:
                display_name += ' '+self.father_name
        if self.family_name:
            display_name += ' '+self.family_name
        self.display_name = display_name

    @api.multi
    def name_get(self):
        res = []
        for emp in self:
            res.append((emp.id, "%s %s %s %s" % (emp.name or '', emp.father_middle_name or '', emp.father_name or '', emp.family_name or '')))
        return res

    @api.one
    def _compute_promotion_days(self):
        active_promotion = self.env['hr.employee.promotion.history'].search([('active_duration', '=', 'True'), ('employee_id', '=', self.id)])
        if active_promotion:
            self.promotion_duration=active_promotion[0].balance

    @api.one
    def _get_first_decision__apoint_date(self):
        decision_appoint_ids = self.decision_appoint_ids
        if decision_appoint_ids:
            direct_action_date = decision_appoint_ids[0].date_direct_action
            for decision_appoint in decision_appoint_ids:
                if fields.Date.from_string(decision_appoint.date_direct_action)<fields.Date.from_string(direct_action_date):
                    direct_action_date=decision_appoint.date_direct_action    
                return direct_action_date
        
    @api.model
    def update_service_duration(self):
        today_date = fields.Date.from_string(fields.Date.today())
        prev_month_end = date(today_date.year, today_date.month, 1) - relativedelta(days=1)
        prev_month_first = prev_month_end.replace(day=1)

        for emp in self.search([ ('state', '=', 'employee')]):
            first_date_direct_action = emp._get_first_decision__apoint_date()
            if first_date_direct_action[0]:
                date_direct_action = fields.Date.from_string(first_date_direct_action[0])
                months = (today_date.year - date_direct_action.year) * 12 + (today_date.month - date_direct_action.month)
                if months < 1:
                    emp.service_duration += (today_date - date_direct_action).days
                else:
                    emp.service_duration += (prev_month_end - prev_month_first).days

                # مدّة غياب‬ ‫الموظف بدون‬ سند‬ ‫ن
                uncounted_absence_days = self.env['hr.attendance.report_day'].search_count([('employee_id', '=', emp.id),('action','=','absence'),
                                                                            ('date','>=',prev_month_first),('date','<=',prev_month_end)])
                emp.service_duration -= uncounted_absence_days

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

    @api.onchange('diploma_id')
    def onchange_diploma_id(self):
        res = {}
        if self.diploma_id:
            specialization_ids = self.diploma_id.specialization_ids.ids
            res['domain'] = {'specialization_ids': [('id', 'in', specialization_ids)]}
        return res



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
        (100, u'طوال مدة الخدمة الوظيفيّة'),
        ], string=u'مدة صلاحيات الإجازة', default=1) 
    entitlement_id = fields.Many2one('hr.holidays.status.entitlement', string=u'نوع الاستحقاق')
    entitlement_name = fields.Char(string=u'نوع الاستحقاق', related='entitlement_id.entitlment_category.name')
    period_id = fields.Many2one('hr.holidays.periode', string=u'periode')


class HrEmployeePromotionHistory(models.Model):
    _name = 'hr.employee.promotion.history'

    employee_id = fields.Many2one('hr.employee', string=u' إسم الموظف')
    salary_grid_id = fields.Many2one('salary.grid.grade', string=u'الرتبة')
    date_from = fields.Date(string=u'التاريخ من', default=fields.Datetime.now())
    date_to = fields.Date(string=u'التاريخ الى')
    balance = fields.Integer(string=u'رصيد الترقية (يوم)',store=True)
    active_duration = fields.Boolean(string=u'نشط')
    decision_appoint_id = fields.Many2one('hr.decision.appoint', string=u'  التعيين')
    
    @api.model
    def update_promotion_duration(self):
        today = date.today()
        prev_month_end = date(today.year, today.month, 1) - relativedelta(days=1)
        prev_month_first = prev_month_end.replace(day=1)
        suspension_obj = self.env['hr.suspension']
        for promotion in self.search([('active_duration','=','True')]):
            if promotion.decision_appoint_id.state_appoint =='active' and promotion.decision_appoint_id.active==True:
                promotion_date_from = fields.Date.from_string(promotion.decision_appoint_id.date_direct_action)
                if promotion.date_from  != promotion_date_from :
                    promotion.date_from  = promotion_date_from 
                months = (today.year - promotion_date_from.year) * 12 + (today.month - promotion_date_from.month)
                if months < 1:
                    promotion.balance += (today - promotion_date_from).days
                else:
                    promotion.balance += (prev_month_end - prev_month_first).days

                # مدّة غياب‬ ‫الموظف بدون‬ سند‬ ‫ن
                uncounted_absence_days = self.env['hr.attendance.report_day'].search_count([('employee_id', '=', promotion.employee_id.id),('action','=','absence'),
                                                                            ('date','>=',prev_month_first),('date','<=',prev_month_end)])
                promotion.balance -= uncounted_absence_days
           

            elif promotion.decision_appoint_id.state_appoint =='close':
                date_hiring_end= fields.Date.from_string(promotion.decision_appoint_id.date_hiring_end)
                promotion.balance += (date_hiring_end - prev_month_first).days
                uncounted_absence_days = self.env['hr.attendance.report_day'].search_count([('employee_id', '=', promotion.employee_id.id),('action','=','absence'),
                                                                            ('date','>=',prev_month_first),('date','<=',date_hiring_end)])
                promotion.balance -= uncounted_absence_days
                promotion.active_duration = False
            elif promotion.decision_appoint_id.state_appoint =='معلق':
                if promotion.employee_id.emp_state == 'suspended':
                    suspension_ids = suspension_obj.search([('employee_id', '=', promotion.employee_id.id),('state', '=','done') ])
                    if suspension_ids:
                        last_suspension = suspension_ids and max(suspension_ids.ids)
                        last_suspension_date = fields.Date.from_string(suspension_obj.browse(last_suspension).suspension_date)
                        if prev_month_first<=last_suspension_date<=prev_month_end:
                            promotion.balance += (last_suspension_date - prev_month_first).days
                            # مدّة غياب‬ ‫الموظف بدون‬ سند‬ ‫ن
                            uncounted_absence_days = self.env['hr.attendance.report_day'].search_count([('employee_id', '=', promotion.employee_id.id),('action','=','absence'),
                                                                            ('date','>=',prev_month_first),('date','<=',last_suspension_date)])
                            promotion.balance -= uncounted_absence_days   
                                     
            suspension_ids = suspension_obj.search([('employee_id', '=', promotion.employee_id.id),('state', '=','done'),
                                                        ('suspension_date','>=',prev_month_first),  ('suspension_date','<=',prev_month_end)])
            if suspension_ids:
                suspension_days = 0
                for suspension in suspension_ids:
                    release_date = fields.Date.from_string(suspension.suspension_end_id.release_date)
                    suspension_date = fields.Date.from_string(suspension.suspension_end_id.suspension_date)
                    if release_date<=prev_month_end:
                        suspension_days += (release_date - suspension_date).days
                promotion.balance -= suspension_days
                                
class HrEmployeeEducationLevel(models.Model):
    _name = 'hr.employee.education.level'  
    _description = u'مستويات التعليم'
  
    name = fields.Char(string=u'الإسم')
    sequence = fields.Char(string=u'الرتبة')
    leave_type = fields.Many2one('hr.holidays.status', string='leave type')
    code = fields.Char(string=u'الرمز')
    
class HrEmployeeDiploma(models.Model):
    _name = 'hr.employee.diploma'  
    _description = u'الشهادة العلمية'

    name = fields.Char(string=u'المسمّى')
    specialization_ids = fields.Many2many('hr.employee.specialization',string=u'الاختصاص')
    code = fields.Char(string=u'الرمز')


class HrEmployeeSpecialization(models.Model):
    _name = 'hr.employee.specialization'  
    _description = u'الاختصاص'
  
    name = fields.Char(string=u'المسمّى')
    code = fields.Char(string=u'الرمز')
    
class HrEmployeeSanction(models.Model):
    _name = 'hr.employee.sanction'  
    _description = u'العقوبات'
  
    employee_id = fields.Many2one('hr.employee', string=' إسم الموظف', )
    type_sanction = fields.Many2one('hr.type.sanction',string='العقوبة',)
    date_sanction_start = fields.Date(string='تاريخ بدأ العقوبة') 
    date_sanction_end = fields.Date(string='تاريخ الإلغاء') 



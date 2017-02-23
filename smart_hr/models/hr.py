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

    @api.multi
    def _compute_holidays_count(self):
        for rec in self:
            rec.holiday_count = self.env['hr.holidays'].search_count([('employee_id', '=', rec.id)])

    
    @api.multi
    def _compute_sanction_count(self):
        for rec in self:
            rec.sanction_count = self.env['hr.sanction'].search_count([('line_ids.employee_id', '=', rec.id)])


    @api.multi
    def _sanction_line(self):
        sanction_obj = self.env['hr.sanction.ligne']
        search_domain = [
                ('employee_id', '=', self.employee_id.id),
                ('state', '=', 'done'),
            ]
        for rec in sanction_obj.search(search_domain): 
            self.sanction_ids = rec.sanction_ids

    number = fields.Char(string=u'الرقم الوظيفي', required=1)
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'),], string=u'الجنس')
    marital =  fields.Selection([('single', 'Single'), ('married', 'Married'), ('widower', 'Widower'), ('divorced', 'Divorced'), ('mariie', 'محصن'), ('not_mariee', 'غير محصن'),('other', 'غير ذلك')], string=u'الجنس')
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
    # Deputation Stock
    deputation_stock = fields.Integer(string=u'الأنتدابات', default=60)
    service_duration = fields.Integer(string=u'مدة الخدمة(يوم)', readonly=True, size=4)
    religion_state = fields.Many2one('religion.religion',string=u'الديانة', required=1)
    emp_state = fields.Selection([('working', u'على رأس العمل'),
                                  ('suspended', u'مكفوف اليد'),
                                   ('outside', u'مكلف خارجي'),
                                  ('terminated', u'مطوي قيده'),
                                  ], string=u'الحالة', default='working', advanced_search=True)
    decision_appoint_ids = fields.One2many('hr.decision.appoint', 'employee_id', string=u'تعيينات الموظف')
    job_id = fields.Many2one('hr.job', advanced_search=True, string=u'الوظيفة')
    type_id = fields.Many2one('salary.grid.type', related="job_id.type_id", advanced_search=True)
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
    father_middle_name = fields.Char(string=u'middle_name', default=u"بن")
    grandfather_middle_name = fields.Char(string=u'middle_name2', default=u"بن")
    grandfather2_middle_name = fields.Char(string=u'  middle_name3', default=u"بن")
    space = fields.Char(string=' ', default=" ", readonly=True)
    begin_work_date = fields.Date(string=u' تاريخ بداية العمل الحكومي', required=1)
    promotion_duration = fields.Integer(string=u'مدة الترقية(يوم)', compute='_compute_promotion_days', store=True)
    dep_city = fields.Many2one('res.city', strin=u'المدينة', related="department_id.dep_city", readonly=True)
    dep_Side = fields.Many2one('city.side', string=u'الجهة', related="department_id.dep_Side", readonly=True)
    history_ids = fields.One2many('hr.employee.history', 'employee_id', string=u'سجل الاجراءات')
    diploma_id = fields.Many2one('hr.employee.diploma', string=u'الشهادة')
    specialization_ids = fields.Many2many('hr.employee.specialization', string=u'التخصص')
    passport_date = fields.Date(string=u'تاريخ إصدار جواز السفر ')
    passport_place = fields.Char(string=u'مكان إصدار جواز السفر')
    passport_end_date = fields.Date(string=u'تاريخ انتهاء جواز السفر ')
    display_name = fields.Char(compute='_compute_display_name', string=u'الاسم', select=True)
    sanction_ids = fields.One2many('hr.sanction.ligne', 'employee_id', string=u'العقوبات' )
    sanction_count = fields.Integer(string=u'عدد  العقوبات',)
    bank_account_ids = fields.One2many('res.partner.bank', 'employee_id', string=u'الحسابات البنكِيّة')
    education_level_ids = fields.One2many('hr.employee.job.education.level', 'employee_id', string=u'المستوى التعليمي')
    education_level_id = fields.Many2one('hr.employee.education.level', string=u'المستوى التعليمي ')
    evaluation_level_ids = fields.One2many('hr.employee.evaluation.level','employee_id', u'التقييم الوظيفي')
    loan_count = fields.Integer(string=u'عدد القروض', compute='_compute_loans_count')
    point_seniority=fields.Integer(string=u'نقاط الأقدمية')
    point_education=fields.Integer(string=u'نقاط التعليم')
    point_training=fields.Integer(string=u'نقاط التدريب')
    point_functionality=fields.Integer(string=u'نقاط  الإداء الوظيفي',)
    is_member = fields.Boolean(string=u'عضو في الهيئة', default=False, required=1)
    insurance_type = fields.Many2one('hr.insurance.type', string=u'نوع التأمين', readonly='1',compute='_compute_insurance_type')
    holiday_count = fields.Integer(string=u'عدد الاجازات', compute='_compute_holidays_count')
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة', readonly=1)
    royal_decree_number = fields.Char(string=u'رقم الأمر الملكي')
    royal_decree_date = fields.Date(string=u'تاريخ الأمر الملكي ')
    training_ids = fields.One2many('hr.candidates', 'employee_id', string=u'سجل التدريبات')
    
    @api.one
    @api.depends('job_id')
    def _compute_insurance_type(self):
        if self.job_id:
            salary_grids = self.env['salary.grid.detail'].search([('type_id', '=', self.job_id.type_id.id),
                                                                  ('grade_id', '=', self.job_id.grade_id.id),
                                                                   ('degree_id', '=', self.degree_id.id)])
            if salary_grids:
                self.insurance_type =  salary_grids[0].insurance_type

    @api.constrains('recruiter_date', 'begin_work_date')
    def recruiter_date_begin_work_date(self):
        if self.recruiter_date < self.begin_work_date:
            raise ValidationError(u"تاريخ بداية العمل الحكومي يجب ان يكون اصغر من تاريخ التعيين بالجهة ")

    @api.one
    @api.depends('name', 'father_middle_name', 'father_name', 'family_name')
    def _compute_display_name(self):
        display_name = self.name
        if self.father_name:
            if self.father_middle_name:
                display_name += ' ' + self.father_middle_name + ' ' + self.father_name
            else:
                display_name += ' ' + self.father_name
        if self.family_name:
            display_name += ' ' + self.family_name
        self.display_name = display_name

    @api.multi
    @api.depends('promotions_history.balance')
    def _compute_promotion_days(self):
        for emp in self:
            active_promotion = self.env['hr.employee.promotion.history'].search([('active_duration', '=', 'True'), ('employee_id', '=', emp.id)], limit=1)
            if active_promotion:
                emp.promotion_duration = active_promotion.balance

    @api.one
    def _get_first_decision__apoint_date(self):
        decision_appoint_ids = self.decision_appoint_ids
        if decision_appoint_ids:
            direct_action_date = decision_appoint_ids[0].date_direct_action
            for decision_appoint in decision_appoint_ids:
                if fields.Date.from_string(decision_appoint.date_direct_action) < fields.Date.from_string(direct_action_date):
                    direct_action_date = decision_appoint.date_direct_action
                return direct_action_date

    @api.model
    def update_service_duration(self):
        today_date = fields.Date.from_string(fields.Date.today())
        prev_month_end = date(today_date.year, today_date.month, 1) - relativedelta(days=1)
        prev_month_first = prev_month_end.replace(day=1)
        for emp in self.search([('state', '=', 'employee')]):
            first_date_direct_action = emp._get_first_decision__apoint_date()
            if first_date_direct_action[0]:
                date_direct_action = fields.Date.from_string(first_date_direct_action[0])
                months = (today_date.year - date_direct_action.year) * 12 + (today_date.month - date_direct_action.month)
                if months < 1:
                    emp.service_duration += (today_date - date_direct_action).days
                else:
                    emp.service_duration += (prev_month_end - prev_month_first).days
                # مدّة غياب‬ ‫الموظف بدون‬ سند‬ ‫ن
                uncounted_absence_days = self.env['hr.attendance.report_day'].search_count([('employee_id', '=', emp.id), ('action', '=', 'absence'),
                                                                                            ('date', '>=', prev_month_first), ('date', '<=', prev_month_end)])
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
    
    
    @api.multi
    def _compute_point(self):
       if self.job_id:
           if self.job_id.grade_id.years_job:
               years_supp=(self.service_duration/365)-self.job_id.grade_id.years_job
               if years_supp > 0 :
                   regle_point=self.env['hr.evaluation.point'].search([('grade_id','=',self.job_id.grade_id)])
                   for seniority in regle_point.seniority_ids:
                       if years_supp < seniority.year_to and years_supp > seniority.year_from:
                           self.point_seniority=years_supp*seniority.point
                           
               
            


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
    date_from = fields.Date(string=u'التاريخ من', default=fields.Datetime.now(), related='decision_appoint_id.date_direct_action')
    date_to = fields.Date(string=u'التاريخ الى', related='decision_appoint_id.date_hiring_end')
    balance = fields.Integer(string=u'رصيد الترقية (يوم)', store=True)
    active_duration = fields.Boolean(string=u'نشط')
    decision_appoint_id = fields.Many2one('hr.decision.appoint', string=u'  التعيين')
    appoint_type = fields.Char(string=u'نوع التعيين')

    @api.model
    def update_promotion_duration(self):
        today = date.today()
        prev_month_end = date(today.year, today.month, 1) - relativedelta(days=1)
        prev_month_first = prev_month_end.replace(day=1)
        active_promotions = self.search([('active_duration', '=', True)])
        for promotion in active_promotions:
            if promotion.decision_appoint_id.state_appoint == 'active' and promotion.decision_appoint_id.is_started is True:
                promotion_date_from = fields.Date.from_string(promotion.decision_appoint_id.date_direct_action)
                months = (today.year - promotion_date_from.year) * 12 + (today.month - promotion_date_from.month)
                if months < 1:
                    promotion.balance += (today - promotion_date_from).days
                else:
                    promotion.balance += (prev_month_end - prev_month_first).days
                # مدّة غياب‬ ‫الموظف بدون‬ سند‬ ‫ن
                uncounted_absence_days = self.env['hr.attendance.report_day'].search_count([('employee_id', '=', promotion.employee_id.id), ('action', '=', 'absence'),
                                                                                            ('date', '>=', prev_month_first), ('date', '<=', prev_month_end)])
                promotion.balance -= uncounted_absence_days

    @api.multi
    def decrement_promotion_duration(self, employee_id, duration_days):
        active_promotions = self.env['hr.employee.promotion.history'].search([('active_duration', '=', 'True'), ('employee_id', '=', employee_id.id)])
        active_prom = False
        if active_promotions:
            for promotion in active_promotions:
                if not promotion.date_to:
                    active_prom = promotion
                    break
        if active_prom:
            active_prom.balance -= duration_days

    @api.multi
    def close_promotion_line(self):
        self.ensure_one()
        promotion_date_from = fields.Date.from_string(self.date_from)
        promotion_date_to = fields.Date.from_string(self.date_to)
        if promotion_date_from and promotion_date_to:
            months = (promotion_date_to.year - promotion_date_from.year) * 12 + (promotion_date_to.month - promotion_date_from.month)
            prom_month_first = promotion_date_to.replace(day=1)
            if months < 1:
                self.balance += (promotion_date_to - promotion_date_from).days
            else:
                self.balance += (promotion_date_to - prom_month_first).days
            self.active_duration = False
            uncounted_absence_days = self.env['hr.attendance.report_day'].search_count([('employee_id', '=', self.employee_id.id), ('action','=', 'absence'),
                                                                                    ('date', '>=', prom_month_first), ('date', '<=', promotion_date_to)])
            self.balance -= uncounted_absence_days


class HrEmployeeEducationLevel(models.Model):
    _name = 'hr.employee.education.level'
    _description = u'مستويات التعليم'

    name = fields.Char(string='المستوى ')
    sequence = fields.Char(string=u'الرتبة')
    leave_type = fields.Many2one('hr.holidays.status', string='leave type')
    code = fields.Char(string=u'الرمز')
    nomber_year_education = fields.Integer(string=u'عدد سنوات الدراسة', )
    diploma_id = fields.Many2one('hr.employee.diploma', string=u'الشهادة')
    specialization_ids = fields.Many2many('hr.employee.specialization', string=u'الاختصاص')
    secondary = fields.Boolean(string=u'بعد‬ الثانوية', required=1)
    not_secondary = fields.Boolean(string=u'قبل الثانوية', required=1)

    @api.onchange('secondary')
    def onchange_secondry(self):
        if self.secondary:
            self.not_secondary = False

    @api.onchange('not_secondary')
    def onchange_not_secondry(self):
        if self.not_secondary:
            self.secondary = False


class HrEmployeeEducationLevelEmployee(models.Model):
    _name = 'hr.employee.job.education.level'
    _description = u'مستويات التعليم'

    name = fields.Char(string='المستوى')
    employee_id = fields.Many2one('hr.employee', string=u' إسم الموظف')
    level_education_id = fields.Many2one('hr.employee.education.level', string=u' مستوى التعليم')
    diploma_id = fields.Many2one('hr.employee.diploma', related='level_education_id.diploma_id', string=u'الشهادة')
    job_specialite = fields.Boolean(string=u'في طبيعة العمل', required=1)
    diploma_date = fields.Date(string=u'تاريخ الحصول على الشهادة')


class HrEmployeeEvaluation(models.Model):
    _name = 'hr.employee.evaluation.level'
    _rec_name = 'degree_id'
    _description = u'التقييم الوظيفي'
    year = fields.Integer(string=u'سنة التقييم', default=int(date.today().year))
    degree_id = fields.Many2one('hr.evaluation.result.foctionality', string=u' الدرجة')
    employee_id = fields.Many2one('hr.employee', string=u'الموظف')


class HrEmployeeDiploma(models.Model):
    _name = 'hr.employee.diploma'
    _description = u'الشهادة العلمية'
    _sql_constraints = [('number_uniq', 'unique(code)', 'رمز هذا المسمى موجود.')]
    
    name = fields.Char(string=u'المسمّى')
    specialization_ids = fields.Many2many('hr.employee.specialization', string=u'التخصص')
    code = fields.Char(string=u'الرمز')


class HrEmployeeSpecialization(models.Model):
    _name = 'hr.employee.specialization'
    _description = u'التخصص'

    name = fields.Char(string=u'المسمّى')
    code = fields.Char(string=u'الرمز')


class HrEmployeeSanction(models.Model):
    _name = 'hr.employee.sanction'
    _description = u'العقوبات'

    employee_id = fields.Many2one('hr.employee', string=' إسم الموظف', )
    type_sanction = fields.Many2one('hr.type.sanction', string='العقوبة')
    date_sanction_start = fields.Date(string='تاريخ بدأ العقوبة')
    date_sanction_end = fields.Date(string='تاريخ الإلغاء') 

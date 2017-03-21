# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from openerp.exceptions import Warning
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from datetime import date
from datetime import date, datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.multi
    def _sanction_line(self):
        sanction_obj = self.env['hr.sanction.ligne']
        search_domain = [
            ('employee_id', '=', self.employee_id.id),
            ('state', '=', 'done'),
        ]
        for rec in sanction_obj.search(search_domain):
            self.sanction_ids = rec.sanction_ids

    number = fields.Char(string=u'رقم الوظيفي')
    gender = fields.Selection([('male', 'Male'), ('female', 'Female'), ], string=u'الجنس')
    marital = fields.Selection(
        [('single', 'Single'), ('married', 'Married'), ('widower', 'Widower'), ('divorced', 'Divorced')],
        string=u'الجنس')
    identification_date = fields.Date(string=u'تاريخ إصدار بطاقة الهوية ')
    identification_place = fields.Many2one('res.city', string=u'مكان إصدار بطاقة الهوية')
    father_name = fields.Char(string=u'إسم الأب', required=1)
    birthday_location = fields.Char(string=u'مكان الميلاد')
    attachments = fields.Many2many('ir.attachment', 'res_id', string=u"المرفقات")
    recruiter = fields.Many2one('recruiter.recruiter', string=u'جهة التوظيف', required=1)
    recruiter_date = fields.Date(string=u' تاريخ التعين بالجهة ')
    employee_state = fields.Selection([('new', u'جديد'),
                                       ('waiting', u'في إنتظار الموافقة'),
                                       ('update', u'إستكمال البيانات'),
                                       ('done', u'اعتمدت'),
                                       ('outside_assignment', u'مكلف خارجي'),
                                       ('non_active', u'مفصول'),
                                       ('oh', u'كف اليد'),
                                       ('retired', u'متقاعد'),
                                       ('employee', u'موظف')], string=u'الحالة', default='new')
    # Deputation Stock
    deputation_balance = fields.Integer(string=u'رصيد الأنتدابات', compute="_compute_deputation_balance")
    service_duration = fields.Integer(string=u'مدة الخدمة(يوم)', readonly=True, size=4)
    religion_state = fields.Many2one('religion.religion', string=u'الديانة', required=1)
    emp_state = fields.Selection([('working', u'على رأس العمل'),
                                  ('suspended', u'مكفوف اليد'),
                                  ('outside', u'مكلف خارجي'),
                                  ('terminated', u'مطوي قيده'),
                                  ], string=u'الحالة', default='working', )
    decision_appoint_ids = fields.One2many('hr.decision.appoint', 'employee_id', string=u'تعيينات الموظف')
    job_id = fields.Many2one('hr.job', string=u'الوظيفة')
    type_id = fields.Many2one('salary.grid.type', string=u'نوع الموظف')
    age = fields.Integer(string=u'السن', compute='_compute_age')
    employee_no = fields.Integer(string=u'رقم الموظف', )
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
    family_name = fields.Char(string=u'الاسم العائلي')
    father_middle_name = fields.Char(string=u'middle_name', default=u"بن")
    grandfather_middle_name = fields.Char(string=u'middle_name2', default=u"بن")
    space = fields.Char(string=' ', default=" ", readonly=True)
    begin_work_date = fields.Date(string=u' تاريخ بداية العمل الحكومي')
    promotion_duration = fields.Integer(string=u'مدة الترقية(يوم)', compute='_compute_promotion_days')
    dep_city = fields.Many2one('res.city', strin=u'المدينة', related="department_id.dep_city", readonly=True)
    dep_side = fields.Many2one('city.side', string=u'الجهة', related="department_id.dep_side", readonly=True)
    history_ids = fields.One2many('hr.employee.history', 'employee_id', string=u'سجل الاجراءات')
    diploma_id = fields.Many2one('hr.employee.diploma', string=u'الشهادة')
    specialization_ids = fields.Many2many('hr.employee.specialization', string=u'التخصص')
    display_name = fields.Char(compute='_compute_display_name', string=u'الاسم', store=True)
    sanction_ids = fields.One2many('hr.sanction.ligne', 'employee_id', string=u'العقوبات')
    sanction_count = fields.Integer(string=u'عدد  العقوبات', )
    bank_account_ids = fields.One2many('res.partner.bank', 'employee_id', string=u'الحسابات البنكِيّة')
    education_level_ids = fields.One2many('hr.employee.job.education.level', 'employee_id', string=u'المستوى التعليمي')
    education_level_id = fields.Many2one('hr.employee.education.level', string=u'المستوى التعليمي ')
    evaluation_level_ids = fields.One2many('hr.employee.evaluation.level', 'employee_id', u'التقييم الوظيفي')
    loan_count = fields.Integer(string=u'عدد القروض', compute='_compute_loans_count')
    point_seniority = fields.Integer(string=u'نقاط الأقدمية')
    point_education = fields.Integer(string=u'نقاط التعليم')
    point_training = fields.Integer(string=u'نقاط التدريب')
    point_functionality = fields.Integer(string=u'نقاط  الإداء الوظيفي', )
    is_member = fields.Boolean(string=u'عضو في الهيئة', default=False,store=True, required=1, compute='_compute_type_id')
    is_saudian = fields.Boolean(string='is saudian', compute='_compute_is_saudian')
    insurance_type = fields.Many2one('hr.insurance.type', string=u'نوع التأمين', readonly='1',
                                     compute='_compute_insurance_type')
    holiday_count = fields.Float(string=u'رصيد الاجازة (يوم)', compute='_compute_holidays_count')
    contracts_count = fields.Integer(string=u'عدد العقود', compute='_compute_contracts_count')
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة', readonly=1)
    royal_decree_number = fields.Char(string=u'رقم الأمر الملكي', readonly=1)
    royal_decree_date = fields.Date(string=u'تاريخ الأمر الملكي ', readonly=1)
    training_ids = fields.One2many('hr.candidates', 'employee_id', string=u'سجل التدريبات')
    state = fields.Selection(selection=[('absent', 'غير مداوم بالمكتب'), ('present', 'مداوم بالمكتب')], string='Attendance')
    employee_card_id = fields.Many2one('hr.employee.functionnal.card')
    residance_id = fields.Char(string=u'رقم الإقامة ')
    residance_date = fields.Date(string=u'تاريخ إصدار بطاقة الإقامة ')
    residance_place = fields.Many2one('res.city', string=u'مكان إصدار بطاقة الإقامة')
    place_of_birth = fields.Many2one('res.city', string=u'مكان الميلاد')
    country_id = fields.Many2one(
        default=lambda self: self.env['res.country'].search([('code_nat', '=', 'SA')], limit=1),
        context="{'compute_name': '_get_natinality'}")
    passport_id = fields.Char(string=u'رقم جواز السفر')
    passport_date = fields.Date(string=u'تاريخ إصدار جواز السفر ')
    passport_place = fields.Many2one('res.city', string=u'مكان إصدار جواز السفر')
    passport_end_date = fields.Date(string=u'تاريخ انتهاء جواز السفر ')
    hoveizeh_id = fields.Char(string=u'رقم الحفيظة')
    hoveizeh_date = fields.Date(string=u'تاريخ إصدار الحفيظة ')
    hoveizeh_place = fields.Many2one('res.city', string=u'مكان إصدار الحفيظة')
    hoveizeh_end_date = fields.Date(string=u'تاريخ انتهاء الحفيظة ')
    mobile_phone = fields.Char(string=u'الجوال')
    is_contract = fields.Boolean(string=u'متعاقد', compute='_compute_is_contract')
    show_mobile = fields.Boolean(string='Show Mobile', compute='_show_mobile', default=True)
    job_number = fields.Char(related="job_id.number", string='الرمز')
    grade_number = fields.Char(related="grade_id.code", string='رقمها')
    service_duration_display = fields.Char(string=u'مدة الخدمة', readonly=True, compute='compute_service_duration_display')
    promotion_duration_display = fields.Char(string=u'مدة الترقية', readonly=True, compute='compute_promotion_duration_display')

    @api.multi
    def compute_service_duration_display(self):
        for rec in self:
            service_duration = rec.service_duration
            years = service_duration // 365
            months = (service_duration % 365) // 30
            days = (service_duration % 365) % 30
            res = str(years) + " سنة و" + str(months) + " أشهر و " + str(days) + "أيام"
            rec.service_duration_display = res

    @api.multi
    def compute_promotion_duration_display(self):
        for rec in self:
            promotion_duration = rec.promotion_duration
            years = promotion_duration // 365
            months = (promotion_duration % 365) // 30
            days = (promotion_duration % 365) % 30
            res = str(years) + " سنة و" + str(months) + " أشهر و " + str(days) + "أيام"
            rec.promotion_duration_display = res

    @api.multi
    def _show_mobile(self):
        for employee in self:
            if self.env.user.has_group('smart_hr.group_hr_personnel_mobile_numbers'):
                employee.show_mobile = True
            if employee.user_id.id == employee._uid:
                employee.show_mobile = True

    @api.multi
    @api.depends('contracts_count')
    def _compute_is_contract(self):
        for rec in self:
            if rec.contracts_count > 0:
                rec.is_contract = True

    @api.multi
    @api.depends('type_id')
    def _compute_type_id(self):
        for rec in self:
            if rec.type_id.is_member is True:
                rec.is_member = True

    @api.multi
    @api.depends('type_id')
    def _compute_deputation_balance(self):
        todayDate = fields.Date.from_string(fields.Date.today())
        year_first_day = todayDate.replace(day=1, month=1)
        year_last_day = todayDate.replace(day=31, month=12)
        for rec in self:
            employee_id = rec.id
            taken_deputations = self.env['hr.deputation'].search([('state', '=', 'done'), ('employee_id', '=', employee_id), ('order_date', '>=', year_first_day), ('order_date', '<=', year_last_day)])
            duration = 0
            for dep in taken_deputations:
                duration += dep.duration
            dep_setting = self.env['hr.deputation.setting'].search([], limit=1)
            if dep_setting:
                rec.deputation_balance = dep_setting.annual_balance - duration

    @api.onchange('gender')
    def _onchange_gender(self):
        if self.gender == 'female':
            self.father_middle_name = u'بنت'
            self.grandfather_middle_name = u'بن'
        else:
            self.father_middle_name = u'بن'
            self.grandfather_middle_name = u'بن'

    @api.multi
    def _compute_loans_count(self):
        for rec in self:
            rec.loan_count = self.env['hr.loan'].search_count([('employee_id', '=', rec.id)])


    @api.multi
    def _compute_holidays_count(self):
        for rec in self:
            stock_line = self.env['hr.employee.holidays.stock'].search([('employee_id', '=', rec.id), ('holiday_status_id', '=', self.env.ref('smart_hr.data_hr_holiday_status_normal').id),
                                                               ], limit=1)
            if stock_line:
                rec.holiday_count = stock_line.holidays_available_stock 
            else:
                rec.holiday_count = 0

    @api.multi
    def _compute_contracts_count(self):
        for rec in self:
            rec.contracts_count = self.env['hr.contract'].search_count([('employee_id', '=', rec.id)])

    @api.multi
    def _compute_sanction_count(self):
        for rec in self:
            rec.sanction_count = self.env['hr.sanction'].search_count([('line_ids.employee_id', '=', rec.id)])

    @api.one
    @api.depends('job_id')
    def _compute_insurance_type(self):
        if self.job_id:
            salary_grids = self.env['salary.grid.detail'].search([('type_id', '=', self.job_id.type_id.id),
                                                                  ('grade_id', '=', self.job_id.grade_id.id),
                                                                  ('degree_id', '=', self.degree_id.id)])
            if salary_grids:
                self.insurance_type = salary_grids[0].insurance_type

    @api.multi
    @api.depends('country_id')
    def _compute_is_saudian(self):
        for rec in self:
            if rec.country_id:
                rec.is_saudian = (rec.country_id.code_nat == 'SA')

    @api.constrains('recruiter_date', 'begin_work_date')
    def recruiter_date_begin_work_date(self):
        if self.recruiter_date < self.begin_work_date:
            raise ValidationError(u"تاريخ بداية العمل الحكومي يجب ان يكون اصغر من تاريخ التعيين بالجهة ")

    @api.onchange('birthday')
    def onchange_birthday(self):
        recruitement_legal_age = self.env['hr.employee.configuration'].search([], limit=1).recruitment_legal_age
        if self.birthday:
            if self.age < recruitement_legal_age:
                raise ValidationError(u"لا يمكن انشاء سجل موظف قبل سن " + str(recruitement_legal_age))

    @api.constrains('birthday')
    def recruitement_legal_age(self):
        recruitement_legal_age = self.env['hr.employee.configuration'].search([], limit=1).recruitment_legal_age
        if self.age < recruitement_legal_age:
            raise ValidationError(u"لا يمكن انشاء سجل موظف قبل سن " + str(recruitement_legal_age))

    @api.multi
    @api.constrains('identification_id', 'residance_id')
    def _check_constraints(self):
        for rec in self:
            if rec.is_saudian and rec.identification_id:
                if len(rec.identification_id) != 10:
                    raise Warning(_('الرجاء التثبت من رقم الهوية.'))
            if not rec.is_saudian and rec.residance_id:
                if len(rec.residance_id) != 10:
                    raise Warning(_('الرجاء التثبت من رقم الإقامة.'))
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

    def _compute_promotion_days(self):
        for rec in self:
            active_promotion = self.env['hr.employee.promotion.history'].search(
                [('active_duration', '=', 'True'), ('employee_id', '=', rec.id)], limit=1)
            if active_promotion:
                rec.promotion_duration = active_promotion.balance


    @api.model
    def update_service_duration(self):
        today_date = fields.Date.from_string(fields.Date.today())
        for emp in self.search([('employee_state', '=', 'employee')]):
            first_decision_appoint_id = self.env['hr.decision.appoint'].search([('state', '=', 'done'),('employee_id', '=', emp.id)], order="date_direct_action asc",limit=1)
            if first_decision_appoint_id:
                first_date_direct_action = first_decision_appoint_id.date_direct_action
                date_direct_action = fields.Date.from_string(first_date_direct_action)
                current_service_duration = emp.service_duration
                if current_service_duration == 0:
                    emp.service_duration = (today_date - date_direct_action).days
                    uncounted_absence_days = self.env['hr.attendance.report_day'].search_count(
                        [('employee_id', '=', emp.id), ('action', '=', 'absence'),
                         ('date', '>=', date_direct_action)])
                else:
                    emp.service_duration += 1
                # مدّة غياب‬ ‫الموظف بدون‬ سند‬ ‫ن
                    uncounted_absence_days = self.env['hr.attendance.report_day'].search_count(
                        [('employee_id', '=', emp.id), ('action', '=', 'absence'),
                         ('date', '=', today_date-relativedelta(days=1))])
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

    @api.onchange('identification_id')
    def onchange_identification_id(self):
        if self.is_saudian and self.identification_id:
            if len(self.identification_id) != 10:
                raise ValidationError(u"الرجاء التثبت من رقم الهوية.")

    @api.onchange('residance_id')
    def onchange_residance_id(self):
        if not self.is_saudian and self.residance_id:
            if len(self.residance_id) != 10:
                raise ValidationError(u"الرجاء التثبت من رقم الإقامة.")

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
        self.employee_state = 'new'

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
                'context': "{'readonly_by_pass': True,'list_type':'_get_dep_name_employee_form','compute_name': '_get_natinality'}"
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
                years_supp = (self.service_duration / 365) - self.job_id.grade_id.years_job
                if years_supp > 0:
                    regle_point = self.env['hr.evaluation.point'].search([('grade_id', '=', self.job_id.grade_id)])
                    for seniority in regle_point.seniority_ids:
                        if seniority.year_to > years_supp > seniority.year_from:
                            self.point_seniority = years_supp * seniority.point


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
    date_from = fields.Date(string=u'التاريخ من', default=fields.Datetime.now(),
                            related='decision_appoint_id.date_direct_action')
    date_to = fields.Date(string=u'التاريخ الى', related='decision_appoint_id.date_hiring_end')
    balance = fields.Integer(string=u'رصيد الترقية (يوم)', store=True)
    active_duration = fields.Boolean(string=u'نشط')
    decision_appoint_id = fields.Many2one('hr.decision.appoint', string=u'  التعيين')
    appoint_type = fields.Char(string=u'نوع التعيين')

    @api.model
    def update_promotion_duration(self):
        today_date = fields.Date.from_string(fields.Date.today())
        active_promotions = self.search([('active_duration', '=', True)])
        for promotion in active_promotions:
            if promotion.decision_appoint_id.state_appoint == 'active' and promotion.decision_appoint_id.is_started is True:
                promotion_date_from = fields.Date.from_string(promotion.decision_appoint_id.date_direct_action)
                current_prom_duration = promotion.balance
                if current_prom_duration == 0:
                    promotion.balance = (today_date - promotion_date_from).days
                    uncounted_absence_days = self.env['hr.attendance.report_day'].search_count(
                        [('employee_id', '=', promotion.employee_id.id), ('action', '=', 'absence'),
                         ('date', '>=', promotion_date_from)])
                else:
                    promotion.balance += 1
                # مدّة غياب‬ ‫الموظف بدون‬ سند‬ ‫ن
                    uncounted_absence_days = self.env['hr.attendance.report_day'].search_count(
                        [('employee_id', '=', promotion.employee_id.id), ('action', '=', 'absence'),
                         ('date', '=', today_date-relativedelta(days=1))])
                promotion.balance -= uncounted_absence_days

    @api.multi
    def decrement_promotion_duration(self, employee_id, duration_days):
        active_promotions = self.env['hr.employee.promotion.history'].search(
            [('active_duration', '=', 'True'), ('employee_id', '=', employee_id.id)])
        active_prom = False
        if active_promotions:
            for promotion in active_promotions:
                if not promotion.date_to:
                    active_prom = promotion
                    break
        if active_prom:
            active_prom.balance -= duration_days



class HrEmployeeEducationLevel(models.Model):
    _name = 'hr.employee.education.level'
    _description = u'مستويات التعليم'

    name = fields.Char(string='المستوى ')
    sequence = fields.Char(string=u'الرتبة')
    leave_type = fields.Many2one('hr.holidays.status', string='leave type')
    code = fields.Char(string=u'الرمز')
    nomber_year_education = fields.Integer(string=u'عدد سنوات الدراسة', )
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

    name = fields.Char(string=u'المستوى')
    employee_id = fields.Many2one('hr.employee', string=u' إسم الموظف')
    level_education_id = fields.Many2one('hr.employee.education.level', string=u' مستوى التعليم')
    diploma_id = fields.Many2one('hr.employee.diploma', string=u'المؤهل')
    specialization_ids = fields.Many2many('hr.employee.specialization', string=u'التخصص')
    qualification_id = fields.Many2one('hr.qualification.estimate', string=u' تقدير المؤهل العلمي')
    governmental_entity = fields.Many2one('res.partner', string=u'المؤسسة العلمية ',
                                          domain=[('company_type', '=', 'school')])
    university_entity = fields.Many2one('res.partner', string=u'الكلية', domain=[('company_type', '=', 'faculty')])
    job_specialite = fields.Boolean(string=u'في طبيعة العمل', required=1)
    diploma_date = fields.Date(string=u'تاريخ الحصول على المؤهل')
    while_serving = fields.Boolean(string=u'اثناء الخدمة', readonly=1)

    @api.onchange('diploma_date')
    def onchange_secondry(self):
        if self.diploma_date >= self.employee_id.recruiter_date:
            self.while_serving = True


class HrQualificationEstimate(models.Model):
    _name = 'hr.qualification.estimate'
    _description = u'تقدير المؤهل العلمي'

    name = fields.Char(string='المسمّى')
    code = fields.Char(string=u'الرمز')


class HrEmployeeConfiguration(models.Model):
    _name = 'hr.employee.configuration'
    _description = u'إعدادات الموظف'

    name = fields.Char(string='name')
    number = fields.Integer(string='بداية تسلسل رقم الوظيفة')
    period = fields.Integer(string='مدة صلاحية بطاقة الموظف (بالسنة)')
    age_member = fields.Integer(string='سن تقاعد  الطبيعي   الاعظاء')
    age_nomember = fields.Integer(string='سن تقاعد  الطبيعي لغير الاعظاء')
    recruitment_legal_age = fields.Integer(string='السن القانوني للتعيين')

    @api.model
    def control_test_retraite_employee(self):
        age_member = self.env.ref('smart_hr.data_hr_employee_configuration').age_member
        age_nomember = self.env.ref('smart_hr.data_hr_employee_configuration').age_nomember
        hr_member = self.env['hr.employee'].search(
            [('emp_state', '!=', 'terminated'), ('employee_state', '=', 'employee')])
        for line in hr_member:
            today_date = fields.Date.from_string(fields.Date.today())
            birthday = fields.Date.from_string(line.birthday)
            years = (today_date - birthday).days / 365
            if years >= age_member and line.is_member:
                self.env['hr.termination'].create({
                    'name': 'تقاعد طبيعي ',
                    'date': today_date,
                    'termination_type_id': self.env.ref('smart_hr.data_hr_ending_service_type_normal').id,
                    'employee_id': line.id,
                    'employee_no': line.number,
                    'job_id': line.job_id.id,
                })
            if years >= age_nomember and not line.is_member:
                self.env['hr.termination'].create({
                    'name': 'تقاعد طبيعي ',
                    'date': today_date,
                    'termination_type_id': self.env.ref('smart_hr.data_hr_ending_service_type_normal').id,
                    'employee_id': line.id,
                    'employee_no': line.number,
                    'job_id': line.job_id.id,
                })

    def send_test_member_group(self, group_id, title, msg):
        """
        :param msg:
        :param title:
        :param group_id:
        """
        for recipient in group_id.users:
            self.env['base.notification'].create({'title': title,
                                                  'message': msg,
                                                  'user_id': recipient.id,
                                                  'show_date': datetime.now().strftime(DEFAULT_SERVER_DATETIME_FORMAT),
                                                  'res_id': self.id,
                                                  'res_action': 'smart_hr.action_hr_decision_appoint',
                                                  'notif': True
                                                  })

    @api.multi
    def button_setting(self):
        hr_employee_configuration_id = self.env['hr.employee.configuration'].search([], limit=1)
        if hr_employee_configuration_id:
            value = {
                'name': u'‫إعدادات الموظف‬‬',
                'view_type': 'form',
                'view_mode': 'form',
                'res_model': 'hr.employee.configuration',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'res_id': hr_employee_configuration_id.id,
            }
            return value


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

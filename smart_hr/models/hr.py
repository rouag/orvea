# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from openerp.exceptions import Warning
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from datetime import date
from datetime import date, datetime, timedelta


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    number = fields.Char(string=u'الرقم الوظيفي', required=1)
    identification_date=fields.Date(string=u'تاريخ إصدار بطاقة الهوية ')
    identification_place=fields.Char(string=u'مكان إصدار بطاقة الهوية')
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
    begin_work_date = fields.Date(string=u' تاريخ بداية العمل بالجهة الحكومية', required=1)
    promotion_duration = fields.Integer(string=u'مدة الترقية(يوم)', compute='_compute_promotion_days')

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
    
    @api.model
    def update_promotion_duration(self):
        today = date.today()
        prev_month_end = date(today.year, today.month, 1) - relativedelta(days=1)
        prev_month_first = prev_month_end.replace(day=1)
        for promotion in self.search([('active_duration','=','True')]):
            promotion_date_from = fields.Date.from_string(promotion.date_from)
            promotion.balance = (today - promotion_date_from).days
            months = (today.year - promotion_date_from.year) * 12 + (today.month - promotion_date_from.month)
            if months < 1:
                promotion.balance += (today - promotion_date_from).days
            else:
                promotion.balance += (prev_month_end - prev_month_first).days

                # مدّة غياب‬ ‫الموظف بدون‬ سند‬ ‫ن
            uncounted_absence_days = self.env['hr.attendance.report_day'].search_count([('employee_id', '=', promotion.employee_id.id),('action','=','absence'),
                                                                            ('date','>=',prev_month_first),('date','<=',prev_month_end)])
            promotion.balance -= uncounted_absence_days

#     def _compute_balance(self):
#         for rec in self:
#             if rec.date_from:
#                 today_date = fields.Date.from_string(fields.Date.today())
#                 date_from = fields.Date.from_string(rec.date_from)
#                 days = (today_date - date_from).days
#                 # find the holidays of the employee start from date_from and they are promotion_deductible
#                 # only deductible_duration_service it means promotion_deductible also
#                 holidays = self.env['hr.holidays'].search([
#                     ('state', '=', 'done'),
#                     ('employee_id', '=', rec.employee_id.id),
#                     ('holiday_status_id.deductible_duration_service', '=', True),
#                     ('date_from', '>=', rec.date_from)
#                     ])
#                 for holiday in holidays:
#                     days -= holiday.periode
# 
#                 rec.balance = days

class HrEmployeeEducationLevel(models.Model):
    _name = 'hr.employee.education.level'  
    _description = u'مستويات التعليم'
  
    name = fields.Char(string=u'الإسم')
    sequence = fields.Char(string=u'الرتبة')
    leave_type = fields.Many2one('hr.holidays.status', string='leave type')

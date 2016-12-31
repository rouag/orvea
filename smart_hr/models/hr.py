# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from openerp.exceptions import Warning
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from datetime import date


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    number = fields.Char(string=u'الرقم الوظيفي', required=1)

    father_name = fields.Char(string=u'إسم الأب', required=1)
    is_resident = fields.Boolean(string=u'موظف مقيم', required=1)
    birthday_location = fields.Char(string=u'مكان الميلاد')
    attachments = fields.Many2many('ir.attachment', 'res_id', string=u"المرفقات")
    recruiter = fields.Many2one('recruiter.recruiter', string=u'جهة التوظيف', required=1)
    employee_state = fields.Selection([('new', u'جديد'),
                                       ('waiting', u'في إنتظار الموافقة'),
                                       ('update', u'إستكمال البيانات'),
                                       ('done', u'اعتمدت'),
                                       ('refused', u'رفض'),
                                       ('employee', u'موظف')], string=u'الحالة', default='new')
    education_level = fields.Many2one('hr.employee.education.level', string=u'المستوى التعليمي')
    # Deputation Stock
    deputation_stock = fields.Integer(string=u'الأنتدابات', default=60)
    service_years = fields.Integer(string=u'سنوات الخدمة', compute='_compute_service_years')
    emp_state = fields.Selection([('working', u'على رأس العمل'),
                                  ('suspended', u'مكفوف اليد'),
                                  ('terminated', u'مطوي قيده'),
                                  ], string=u'الحالة', default='working', advanced_search=True)
    job_id = fields.Many2one(advanced_search=True)
    age = fields.Integer(string=u'السن', compute='_compute_age')
    employee_no = fields.Integer(string=u'رقم الموظف', advanced_search=True)
    join_date = fields.Date(string=u'تاريخ الالتحاق بالجهة')
    external_decision = fields.Boolean(string=u'موافقة خارجية', default=False)
    holidays = fields.One2many('hr.holidays', 'employee_id', string=u'الاجازات')
    holidays_balance = fields.One2many('hr.employee.holidays.stock', 'employee_id', string=u'الأرصدة', readonly=1)
    promotions_history = fields.One2many('hr.employee.promotion.history', 'employee_id', string=u'الترقيات')
    traveling_ticket = fields.Boolean(string=u'تذكرة سفر', default=False)
    traveling_ticket_familiar = fields.Boolean(string=u'تذكرة سفر عائليّة', default=False)
    compensation_stock = fields.Integer(string=u'رصيد إجازات التعويض')
    sick_holiday_peiodes = fields.One2many('hr.illness.holidays.periode', 'employee_id', string='sick holidays periodes')
    
    def _compute_service_years(self):
        for emp in self:
            decision_appoint = self.env['hr.decision.appoint'].search([('state', '=', 'done'), ('employee_id', '=', emp.id)])
            if decision_appoint:
                today_date = fields.Date.from_string(fields.Date.today())
                date_hiring = fields.Date.from_string(decision_appoint[0].date_hiring)
                days = (today_date - date_hiring).days
                deductible_days = 0
                # find the holidays of the employee that are deductible_duration_service and promotion_deductible
                holidays = self.env['hr.holidays'].search([
                    ('state', '=', 'done'),
                    ('employee_id', '=', emp.id),
                    ('holiday_status_id.deductible_duration_service', '=', True), ('holiday_status_id.promotion_deductible', '=', True),
                    ])
                # find the holidays of the employee that are only promotion_deductible
                holidays += self.env['hr.holidays'].search([
                    ('state', '=', 'done'),
                    ('employee_id', '=', emp.id),
                    ('holiday_status_id.deductible_duration_service', '=', False), ('holiday_status_id.promotion_deductible', '=', True),
                    ])
                for holiday in holidays:
                    days -= holiday.duration
                years = days / 365
                if years > -1:
                    emp.service_years = years



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
        ], string=u'مدة صلاحيات الإجازة', default=1) 

class HrEmployeePromotionHistory(models.Model):
    _name = 'hr.employee.promotion.history'

    employee_id = fields.Many2one('hr.employee', string=u' إسم الموظف')
    salary_grid_id = fields.Many2one('salary.grid.grade', string=u'الرتبة')
    date_from = fields.Date(string=u'التاريخ من', default=fields.Datetime.now())
    date_to = fields.Date(string=u'التاريخ الى')
    balance = fields.Integer(string=u'رصيد الترقية (يوم)', compute='_compute_balance',store=True)

    def _compute_balance(self):
        for rec in self:
            if rec.date_from:
                today_date = fields.Date.from_string(fields.Date.today())
                date_from = fields.Date.from_string(rec.date_from)
                days = (today_date - date_from).days
                # find the holidays of the employee start from date_from and they are promotion_deductible
                # only deductible_duration_service it means promotion_deductible also
                holidays = self.env['hr.holidays'].search([
                    ('state', '=', 'done'),
                    ('employee_id', '=', rec.employee_id.id),
                    ('holiday_status_id.deductible_duration_service', '=', True),
                    ('date_from', '>=', rec.date_from)
                    ])
                for holiday in holidays:
                    days -= holiday.periode

                rec.balance = days
 
            
class HrEmployeeEducationLevel(models.Model):
    _name = 'hr.employee.education.level'  
    _description = u'مستويات التعليم'
  
    name = fields.Char(string=u'الإسم')
    sequence = fields.Char(string=u'الرتبة')
    leave_type = fields.Many2one('hr.holidays.status', string='leave type')

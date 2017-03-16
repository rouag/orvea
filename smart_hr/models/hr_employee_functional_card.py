# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from datetime import date, datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class HrEmployeeFunctionnalCard(models.Model):
    _name = 'hr.employee.functionnal.card'
    _inherit = ['mail.thread']
    _description = u'بطاقة موظف'

    @api.multi
    @api.depends('department_id')
    def _get_department_name_report(self):
        for card in self:
            department_name_report = card.department_id._get_dep_name_employee_form()[0]
            card.department_name_report = department_name_report[1]

    name = fields.Char(string='رقم بطاقة')
    employee_id = fields.Many2one('hr.employee', string=u'الموظف', required=1, readonly=1)
    number = fields.Char(string=u'رقم الوظيفة', related="employee_id.number", readonly=1)
    employee_state = fields.Selection(string=u'الحالة', related="employee_id.employee_state", readonly=1)
    last_salary = fields.Float(string='  الراتب الأخير ', store=True, compute='_compute_last_degree_salary', readonly=1)
    birthday_location = fields.Char(string=u'مكان الميلاد', related="employee_id.birthday_location", readonly=1)
    birthday = fields.Date(string=u'تاريخ الميلاد', related="employee_id.birthday", readonly=1)
    degree_id = fields.Many2one('salary.grid.degree', string='الدرجة', compute='_compute_last_degree_salary',
                                readonly=1)
    identification_id = fields.Char(string=u'رقم الهوية', related="employee_id.identification_id", readonly=1)
    passport_id = fields.Char(string=u'رقم الحفيظة', related="employee_id.passport_id", readonly=1)
    join_date = fields.Date(string=u'تاريخ الالتحاق بالجهة', related="employee_id.join_date", readonly=1)
    begin_work_date = fields.Date(string=u' تاريخ بداية العمل الحكومي', related="employee_id.begin_work_date",
                                  readonly=1)
    specialization_ids = fields.Many2many('hr.employee.specialization', string=u'التخصص',
                                          related='education_level.specialization_ids', readonly=1)
    education_level = fields.Many2one('hr.employee.education.level', compute='_compute_education_level',
                                      string=u'المستوى التعليمي', readonly=1)
    history_ids = fields.One2many('hr.employee.history', 'employee_id', string=u'سجل الاجراءات',
                                  related="employee_id.history_ids", readonly=1)
    emp_name = fields.Char(string=u'إسم الموظف', related="employee_id.display_name", readonly=1)
    emp_age = fields.Integer(string=u'السن', related="employee_id.age", readonly=1)
    department_id = fields.Many2one('hr.department', string=u'مكان العمل', related="employee_id.department_id",
                                    readonly=1)
    passport_date = fields.Date(string=u'تاريخ إصدار الحفيظة ', related='employee_id.passport_date', readonly=1)
    passport_place = fields.Many2one('res.city', string=u'مكان إصدار الحفيظة', related='employee_id.passport_place',
                                     readonly=1)
    date = fields.Date(string=u'التاريخ ', default=fields.Datetime.now(), readonly=1)
    start_date = fields.Date(string=u'تاريخ بدأ الصلاحية  ', readonly=1)
    end_date = fields.Date(string=u'تاريخ إنتهاء الصلاحية ', readonly=1)
    state = fields.Selection([('draft', u'طلب'),
                              ('hrm', u'مدير شؤون الموظفين'),
                              ('done', u'اعتمدت'),
                              ('refuse', u'رفض'),
                              ], string=u'الحالة', default='draft', )
    training_ids = fields.One2many('hr.candidates', 'employee_id', string=u'التدريب', readonly=1,
                                   related="employee_id.training_ids")
    department_name_report = fields.Char(compute=_get_department_name_report, store=True)

    @api.multi
    @api.depends('employee_id')
    def _compute_education_level(self):
        for card in self:
            employee_id = card.employee_id
            emp_level_ids = employee_id.education_level_ids
            for level in reversed(emp_level_ids):
                if level.job_specialite:
                    self.education_level = level.level_education_id.id
                    break

    @api.one
    @api.depends('employee_id')
    def _compute_last_degree_salary(self):
        last_decision_appoint = self.env['hr.decision.appoint'].search(
            [('employee_id', '=', self.employee_id.id), ('state_appoint', '=', 'active')], limit=1)
        if last_decision_appoint:
            self.last_salary = last_decision_appoint.basic_salary
            self.degree_id = last_decision_appoint.degree_id.id

    @api.model
    def create(self, vals):
        res = super(HrEmployeeFunctionnalCard, self).create(vals)
        vals['name'] = self.env['ir.sequence'].get('hr.employye.card.seq')
        res.write(vals)
        return res

    @api.multi
    def button_accept_hrm(self):
        self.ensure_one()
        self.start_date = fields.Datetime.now()
        employee_card = self.env['hr.employee.functionnal.card'].search(
            [('employee_id', '=', self.employee_id.id), ('end_date', '>=', self.start_date)], limit=1)
        if employee_card:
            self.start_date = self.start_date
            self.end_date = employee_card.end_date
            self.employee_id.write({'employee_card_id': self.id})

        else:
            card_validity = self.env['hr.employee.configuration'].search([], limit=1)
            if card_validity:
                periode_validity = card_validity.period
                self.start_date = fields.Datetime.now()
                self.end_date = (fields.Date.from_string(self.start_date) + relativedelta(years=+int(periode_validity)))
                self.employee_id.write({'employee_card_id': self.id})
        self.state = 'done'

    @api.multi
    def button_send_request(self):
        self.ensure_one()
        self.state = 'hrm'

    @api.multi
    def button_refuse(self):
        self.ensure_one()
        self.state = 'refuse'

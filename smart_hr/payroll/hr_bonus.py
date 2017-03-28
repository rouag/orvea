# -*- coding: utf-8 -*-

from openerp import models, api, fields, _
from openerp.exceptions import ValidationError
from datetime import date, datetime, timedelta
from openerp.addons.smart_base.util.umalqurra import *


class hrBonus(models.Model):
    _name = 'hr.bonus'
    _inherit = ['mail.thread']
    _order = 'id desc'
    _description = u'المزايا المالية'

    # TODO: must add current year

    name = fields.Char(string=' المسمى', required=1, readonly=1, states={'new': [('readonly', 0)]})
    number_decision = fields.Char(string='رقم القرار', required=1, readonly=1, states={'new': [('readonly', 0)]})
    date_decision = fields.Date(string=' تاريخ القرار', required=1, readonly=1, states={'new': [('readonly', 0)]})
    date = fields.Date(string=' التاريخ ', required=1, readonly=1, states={'new': [('readonly', 0)]})
    period_from_id = fields.Many2one('hr.period', string='الفترة', required=1, readonly=1, states={'new': [('readonly', 0)]})
    period_to_id = fields.Many2one('hr.period', string='إلى', required=1, readonly=1, states={'new': [('readonly', 0)]})
    type = fields.Selection([('allowance', 'بدل'), ('reward', 'مكافأة'), ('indemnity', 'تعويض'), ('increase', 'علاوة')], string='النوع', required=1, readonly=1, states={'new': [('readonly', 0)]})
    allowance_id = fields.Many2one('hr.allowance.type', string='البدل', readonly=1, states={'new': [('readonly', 0)]})
    reward_id = fields.Many2one('hr.reward.type', string='المكافأة', readonly=1, states={'new': [('readonly', 0)]})
    indemnity_id = fields.Many2one('hr.indemnity.type', string='التعويض', readonly=1, states={'new': [('readonly', 0)]})
    increase_id = fields.Many2one('hr.increase.type', string='العلاوة', readonly=1, states={'new': [('readonly', 0)]})
    
    compute_method = fields.Selection([('amount', 'مبلغ'),
                                       ('percentage', 'نسبة من الراتب الأساسي'),
                                       ('formula_1', 'نسبة‬ البدل‬ * راتب‬  الدرجة‬ الاولى‬  من‬ المرتبة‬  التي‬ يشغلها‬ الموظف‬'),
                                       ('formula_2', 'نسبة‬ البدل‬ * راتب‬  الدرجة‬ التي ‬ يشغلها‬ الموظف‬'),
                                       ('job_location', 'تحتسب  حسب مكان العمل')], required=1, string='طريقة الإحتساب')
    amount = fields.Float(string='المبلغ')
    min_amount = fields.Float(string='الحد الأدنى')
    percentage = fields.Float(string='النسبة')
    city_ids = fields.One2many('hr.bonus.city', 'bonus_id', string='النسب حسب المدينة')
    state = fields.Selection([('new', 'طلب'),
                              ('waiting', 'في إنتظار الإعتماد'),
                              ('cancel', 'مرفوض'),
                              ('done', 'اعتمدت')], string='الحالة', readonly=1, default='new')
    line_ids = fields.One2many('hr.bonus.line', 'bonus_id', string='التفاصيل', readonly=1, states={'new': [('readonly', 0)]})
    history_ids = fields.One2many('hr.bonus.history', 'bonus_id', string='سجل التغييرات', readonly=1)
    deccription = fields.Char(string='ملاحظات', )

    @api.onchange('period_from_id', 'period_to_id')
    def onchange_date(self):
        if self.period_from_id and self.period_to_id and self.period_from_id.date_stop > self.period_to_id.date_stop:
            self.period_to_id = False
            warning = {'title': _('تحذير!'), 'message': _(u'الرجاء التثبت من الفترة المختارة')}
            return {'warning': warning}

    @api.one
    def action_waiting(self):
        self.state = 'waiting'

    @api.multi
    def action_done(self):
        if self.type == 'increase':
            for line in self.line_ids:
                self.env['hr.employee.history'].sudo().add_action_line(line.employee_id, self.number_decision, self.date_decision, "علاوة")
        self.state = 'done'

    @api.one
    def button_refuse(self):
        self.state = 'cancel'

    @api.multi
    def import_employee_beneficiaries_ids(self):
        self.ensure_one()
        line_ids = self.line_ids
        employee_ids = []
        increase_ids = self.env['hr.employee.increase.percent'].search([('increase_id.date', '<=', datetime.now()),
                                                                        ('increase_id.date', '>=', datetime.now().replace(day=1, month=1)),
                                                                        ('increase_id.state', '=', 'done'),
                                                                        ('increase_percent', '=', self.percentage)])
        for emp in increase_ids:
            self.env['hr.bonus.line'].create({'bonus_id': self.id,
                                              'employee_id': emp.employee_id.id,
                                              'compute_method': self.compute_method,
                                              'period_from_id': self.period_from_id.id,
                                              'period_to_id': self.period_to_id.id,
                                              })


class hrBonusCity(models.Model):
    _name = 'hr.bonus.city'

    bonus_id = fields.Many2one('hr.bonus', string='المزايا المالية', ondelete='cascade')
    city_id = fields.Many2one('res.city', string='المدينة', required=1)
    percentage = fields.Float(string='النسبة', required=1)


class hrBonusLine(models.Model):
    _name = 'hr.bonus.line'
    _description = u'تفاصيل المزايا المالية'

    bonus_id = fields.Many2one('hr.bonus', string='المزايا المالية', ondelete='cascade')
    name = fields.Char(string='المسمى')
    employee_id = fields.Many2one('hr.employee', string='الموظف', required=1)
    number = fields.Char(related='employee_id.number', store=True, readonly=True, string=' رقم الوظيفة')
    job_id = fields.Many2one(related='employee_id.job_id', store=True, readonly=True, string=' الوظيفة')
    department_id = fields.Many2one(related='employee_id.department_id', store=True, readonly=True, string=' الادارة')
    type = fields.Selection(related='bonus_id.type', store=True, string='النوع')
    bonus_state = fields.Selection(related='bonus_id.state', store=True, string='الحالة')
    allowance_id = fields.Many2one('hr.allowance.type', string='البدل')
    reward_id = fields.Many2one('hr.reward.type', string='المكافأة')
    indemnity_id = fields.Many2one('hr.indemnity.type', string='التعويض')
    increase_id = fields.Many2one('hr.increase.type', string='العلاوة')
    period_from_id = fields.Many2one('hr.period', string='الفترة', required=1, readonly=1, states={'new': [('readonly', 0)]})
    period_to_id = fields.Many2one('hr.period', string='إلى', required=1, readonly=1, states={'new': [('readonly', 0)]})
    amount = fields.Float(string='القيمة')
    percentage = fields.Float(string='النسبة')
    min_amount = fields.Float(string='الحد الأدنى')
    compute_method = fields.Selection([('amount', 'مبلغ'),
                                       ('percentage', 'نسبة من الراتب الأساسي'),
                                       ('salary_grid', 'تحتسب من سلم الرواتب'),
                                       ('job', 'تحتسب من  الوظيفة'),
                                       ('job_location', 'تحتسب  حسب مكان العمل')], string='طريقة الإحتساب', required=1)
    state = fields.Selection([('progress', 'ساري'),
                              ('stop', 'إيقاف'),
                              ('expired', 'منتهي')
                              ], string='الحالة', readonly=1, default='progress')

    @api.model
    def get_value(self, employee_id):
        bonus_city_obj = self.env['hr.bonus.city']
        degree_obj = self.env['salary.grid.degree']
        salary_grid_obj = self.env['salary.grid.detail']
        # employee info
        employee = self.env['hr.employee'].browse(employee_id)
        ttype = employee.job_id.type_id
        grade = employee.job_id.grade_id
        degree = employee.degree_id
        amount = 0.0
        # search the correct salary_grid for this employee
        salary_grids, basic_salary = employee.get_salary_grid_id(False)
        if not salary_grids:
            return
        basic_salary = basic_salary
        # compute
        if self.compute_method == 'amount':
            amount = self.amount
        if self.compute_method == 'percentage':
            amount = self.percentage * basic_salary / 100.0
        if self.compute_method == 'job_location':
            if employee.dep_city:
                citys = bonus_city_obj.search([('bonus_id', '=', self.bonus_id.id), ('city_id', '=', employee.dep_city.id)])
                if citys:
                    amount = citys[0].percentage * basic_salary / 100.0
        if self.compute_method == 'formula_1':
            # get first degree for the grade
            degrees = degree_obj.search([('grade_id', '=', grade.id)])
            if degrees:
                salary_grids = salary_grid_obj.search([('type_id', '=', ttype.id), ('grade_id', '=', grade.id), ('degree_id', '=', degrees[0].id)])
                if salary_grids:
                    amount = basic_salary * self.percentage / 100.0
        if self.compute_method == 'formula_2':
            amount = self.percentage * basic_salary / 100.0
        if self.min_amount and amount < self.min_amount:
            amount = self.min_amount
        return amount


class hrBonusHistory(models.Model):
    _name = 'hr.bonus.history'

    bonus_id = fields.Many2one('hr.bonus', string='المزايا المالية', ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string=' الموظف', required=1)
    action = fields.Char(string='الإجراء')
    reason = fields.Char(string='السبب', required=1,)
    number_decision = fields.Char(string='رقم القرار')
    date_decision = fields.Date(string='تاريخ القرار')

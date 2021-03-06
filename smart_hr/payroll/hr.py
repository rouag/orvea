# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    degree_id = fields.Many2one('salary.grid.degree', string=u'الدرجة')
    salary_increase_ids = fields.One2many('employee.increase', 'employee_id', string=u'العلاوات')
    # basic salary for retired employee
    basic_salary = fields.Float(string=u'الراتب الأساسي', default=0)
    net_salary = fields.Float(string=u'صافي الراتب', compute='_compute_net_salary')
    hr_employee_allowance_ids = fields.One2many('hr.employee.allowance', 'employee_id', readonly=1)
    to_be_clear_financial_dues = fields.Boolean(string='سيأخذ مستحقاته المالية فحلت طي قيده', defaul=False)
    clear_financial_dues = fields.Boolean(string='أخذ مستحقاته المالية فحلت طي قيده', defaul=False)
    hr_changement_ids = fields.One2many('hr.employee.payroll.changement', 'employee_id')

    @api.multi
    def _compute_net_salary(self):
        for rec in self:
            salary_grid_id, basic_salary = rec.get_salary_grid_id(False)
            if salary_grid_id:
                rec.net_salary = salary_grid_id.net_salary

    @api.model
    def get_employee_allowances(self, salary_grid_id):
        """
        @param: operation_date: to bring the right salary grid of the date
        @return: Array of dict of allowance and it's amount
        """
        res = []
        if salary_grid_id:
                active_decision_appoint = self.env['hr.decision.appoint'].search([('employee_id', '=', self.id),
                                                                                  ('state_appoint', '=', 'active'), ('is_started', '=', True)
                                                                                  ], order="date_direct_action desc", limit=1)
                # allowances from employee's salary grid
                for allowance in salary_grid_id.allowance_ids:
                    # dont calculate transport allowance if the employee have a car
                    if not (active_decision_appoint.transport_car and allowance.allowance_id == self.env.ref('smart_hr.hr_allowance_type_01')):
                        amount = allowance.get_value(self.id)
                        res.append({'allowance_name': allowance.allowance_id.name, 'allowance_id': allowance.allowance_id.id, 'amount': amount})
                # allowance from employee
                for line in self.hr_employee_allowance_ids:
                    if line.salary_grid_detail_id == salary_grid_id:
                        res.append({'allowance_name': line.allowance_id.name,
                                    'allowance_id': line.allowance_id.id,
                                    'amount': line.amount})
        return res

    @api.model
    def get_salary_grid_id(self, operation_date):
        '''
        @return:  two values value1: salary grid detail, value2: basic salary
        '''
        basic_salary = 0.0
        # search for  the newest salary grid detail
        domain = [('employee_id', '=', self.id),
                  ]
        if operation_date:
            # search the right salary grid detail for the given operation_date
            domain.append(('date', '<=', operation_date))
        changement_line = self.env['hr.employee.payroll.changement'].search(domain, order='date desc', limit=1)
        # doamin for  the newest salary grid detail
        if not changement_line and len(domain) == 2:
            domain.pop(1)
            changement_line = self.env['hr.employee.payroll.changement'].search(domain, order='date desc', limit=1)
        # default salary is from curent employee
        type_id = self.type_id
        grade_id = self.grade_id
        degree_id = self.degree_id
        if changement_line:
            type_id = changement_line.type_id
            grade_id = changement_line.grade_id
            degree_id = changement_line.degree_id

        # search grid
        grid_domain = [('grid_id.state', '=', 'done'),
                       ('grid_id.enabled', '=', True),
                       ('type_id', '=', type_id.id),
                       ('grade_id', '=', grade_id.id),
                       ('degree_id', '=', degree_id.id)]
        if operation_date:
            grid_domain.append(('date', '<=', operation_date))
        salary_grid_detail_id = self.env['salary.grid.detail'].search(grid_domain, order='date desc', limit=1)
        if not salary_grid_detail_id and len(grid_domain) == 6:
            grid_domain.pop(5)
        salary_grid_detail_id = self.env['salary.grid.detail'].search(grid_domain, order='date desc', limit=1)
        if salary_grid_detail_id:
            # retreive old salary increases to add them with basic_salary
            domain = [('salary_grid_detail_id', '=', salary_grid_detail_id.id)]
            if operation_date:
                domain.append(('date', '<=', operation_date))
            salary_increase_ids = self.env['employee.increase'].search(domain)
            sum_increases_amount = 0.0
            for rec in salary_increase_ids:
                sum_increases_amount += rec.amount
            if self.basic_salary == 0:
                basic_salary = salary_grid_detail_id.basic_salary + sum_increases_amount
            else:
                basic_salary = self.basic_salary + sum_increases_amount
        return salary_grid_detail_id, basic_salary


class HrEmployeeAllowance(models.Model):
    _name = 'hr.employee.allowance'

    employee_id = fields.Many2one('hr.employee', string='الموظف')
    allowance_id = fields.Many2one('hr.allowance.type', string='البدل', required=1)
    amount = fields.Float(string='المبلغ')
    date = fields.Date(string='التاريخ')
    salary_grid_detail_id = fields.Many2one('salary.grid.detail', string='تفاصيل سلم الرواتب')


class HrEmployeePayrollChangement(models.Model):
    _name = 'hr.employee.payroll.changement'

    employee_id = fields.Many2one('hr.employee', string='الموظف')
    date = fields.Date(string='التاريخ')
    degree_id = fields.Many2one('salary.grid.degree', string='الدرجة', required=1)
    grade_id = fields.Many2one('salary.grid.grade', string='المرتبة')
    type_id = fields.Many2one('salary.grid.type', string='الصنف')


class EmployeeIncrease(models.Model):
    _name = 'employee.increase'

    name = fields.Char(string='المسمى')
    amount = fields.Float(string='المبلغ', required=1)
    salary_grid_detail_id = fields.Many2one('salary.grid.detail', string='تفاصيل سلم الرواتب')
    date = fields.Date(string='التاريخ')
    employee_id = fields.Many2one('hr.employee')

#     @api.model
#     def update_salary_increases(self):
#         employee_ids = self.env['hr.employee'].search([('employee_state', '=', 'employee')])
#         res = []
#         for emp in employee_ids:
#             salary_grid_line_id, basic_salary = emp.get_salary_grid_id(False)
#             increase_amout = salary_grid_line_id.increase
#             if increase_amout > 0:
#                 employee_amount = {'employee_id': emp.id, 'amount': increase_amout}
#                 res.append(employee_amount)
#         for rec in res:
#             employee_id = rec.get('employee_id')
#             amount = rec.get('amount')
#             self.env['employee.increase'].create({'name': u'علاوة سنوية',
#                                                 'employee_id': employee_id,
#                                                 'amount': amount,
#                                                 'date':
#                                                 })
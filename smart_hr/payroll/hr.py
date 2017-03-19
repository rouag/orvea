# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp
from openerp.exceptions import ValidationError


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    degree_id = fields.Many2one('salary.grid.degree', string=u'الدرجة')
    salary_increase_ids = fields.One2many('salary.increase', 'employee_id', string=u'العلاوات')
    # basic salary for retired employee
    basic_salary = fields.Float(string=u'الراتب الأساسي', default=0)
    net_salary = fields.Float(string=u'صافي الراتب', compute='_compute_net_salary')
    hr_employee_allowance_ids = fields.One2many('hr.employee.allowance', 'employee_id', readonly=1)

    @api.multi
    def _compute_net_salary(self):
        for rec in self:
            salary_grid_id, basic_salary = rec.get_salary_grid_id(False)
            if salary_grid_id:
                rec.net_salary = salary_grid_id.net_salary

    @api.model
    def get_salary_grid_id(self, operation_date):
        '''
        @return:  two values value1: salary grid detail, value2: basic salary
        '''
        # search for  the newest salary grid detail
        domain = [('grid_id.state', '=', 'done'),
                  ('grid_id.enabled', '=', True),
                  ('type_id', '=', self.type_id.id),
                  ('grade_id', '=', self.grade_id.id),
                  ('degree_id', '=', self.degree_id.id)
                  ]
        if operation_date:
            # search the right salary grid detail for the given operation_date
            domain.append(('date', '<=', operation_date))
        salary_grid_id = self.env['salary.grid.detail'].search(domain, order='date desc', limit=1)
        if not salary_grid_id:
            # doamin for  the newest salary grid detail
            if len(domain) == 6:
                domain.pop(5)
            salary_grid_id = self.env['salary.grid.detail'].search(domain, order='date desc', limit=1)
        # retreive old salary increases to add them with basic_salary
        domain = [('salary_grid_detail_id', '=', salary_grid_id.id)]
        if operation_date:
            domain.append(('date', '<=', operation_date))
        salary_increase_ids = self.env['salary.increase'].search(domain)
        sum_increases_amount = 0.0
        for rec in salary_increase_ids:
            sum_increases_amount += rec.amount
        if self.basic_salary == 0:
            basic_salary = salary_grid_id.basic_salary + sum_increases_amount
        else:
            basic_salary = self.basic_salary + sum_increases_amount
        return salary_grid_id, basic_salary


class HrEmployeeAllowance(models.Model):
    _name = 'hr.employee.allowance'

    employee_id = fields.Many2one('hr.employee', string='الموظف')
    allowance_id = fields.Many2one('hr.allowance.type', string='البدل', required=1)
    amount = fields.Float(string='المبلغ')
    date = fields.Date(string='التاريخ')
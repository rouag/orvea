# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    degree_id = fields.Many2one('salary.grid.degree', string=u'الدرجة')
    salary_increase_ids = fields.One2many('salary.increase', 'employee_id', string=u'العلاوات')
    # basic salary for retired employee
    basic_salary = fields.Float(string=u'الراتب الأساسي', default=0)
    net_salary = fields.Float(string=u'صافي الراتب', compute='_compute_net_salary')

    @api.multi
    def _compute_net_salary(self):
        for rec in self:
            salary_grid_id = rec.get_salary_grid_id(False)[0]
            if salary_grid_id:
                rec.net_salary = salary_grid_id.net_salary

    @api.model
    def get_salary_grid_id(self, operation_date):
        '''
        @return: array of two colum res[0]: salary grid detail, res[1]: basic salary
        '''
        res = []
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
        res.append(salary_grid_id)
        return res

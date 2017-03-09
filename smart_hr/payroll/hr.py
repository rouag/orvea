# -*- coding: utf-8 -*-
from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    degree_id = fields.Many2one('salary.grid.degree', string='الدرجة')
    # basic salary for retired employee
    basic_salary = fields.Float(string='الراتب الأساسي', default=0)

    @api.model
    def get_salary_grid_id(self, operation_date):
        if not operation_date:
            # return the newest salary grid detail
            salary_grid_id = self.env['salary.grid.detail'].search([('grid_id.enabled', '=', True),
                                                                    ('type_id', '=', self.type_id.id),
                                                                    ('grade_id', '=', self.grade_id.id),
                                                                    ('degree_id', '=', self.degree_id.id)
                                                                    ], order='date desc', limit=1)
        if operation_date:
            # return the right salary grid detail for the given operation_date
            salary_grid_id = self.env['salary.grid.detail'].search([('grid_id.enabled', '=', True),
                                                                    ('type_id', '=', self.type_id.id),
                                                                    ('grade_id', '=', self.grade_id.id),
                                                                    ('degree_id', '=', self.degree_id.id),
                                                                    ('date', '<=', operation_date)
                                                                    ], order='date desc', limit=1)
        return salary_grid_id

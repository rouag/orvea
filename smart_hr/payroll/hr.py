# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.one
    @api.depends('job_id', 'type_id', 'degree_id', 'grade_id')
    def _get_salary_grid_id(self):
        if self.type_id and self.grade_id and self.degree_id:
            salary_grids = self.env['salary.grid.detail'].search([('type_id', '=', self.type_id.id), ('grade_id', '=', self.grade_id.id), ('degree_id', '=', self.degree_id)])
            if salary_grids:
                return salary_grids[0]
        return False

    degree_id = fields.Many2one('salary.grid.degree', string='الدرجة')
    salary_grid_id = fields.Many2one('salary.grid.detail', string='سلم الرواتب', compute='_get_salary_grid_id')

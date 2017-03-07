# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    degree_id = fields.Many2one('salary.grid.degree', string='الدرجة')
    salary_grid_id = fields.Many2one('salary.grid.detail', string='سلم الرواتب')
    # basic salary for retired employee
    basic_salary = fields.Float(string='الراتب الأساسي', default=0) 

# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
import openerp.addons.decimal_precision as dp


class HrEmployee(models.Model):
    _inherit = 'hr.employee'

    @api.one
    @api.depends('allowance_ids.allowance_id', 'allowance_ids.amount', 'allowance_ids.employee_id')
    def _compute_allowance_transport(self):
        # TODO:
        self.allowance_transport = 5.0
        self.allowance_house = 6.0

    payroll_structure_id = fields.Many2one('hr.payroll.structure', 'هيكل الراتب')
    wage = fields.Float(string='الراتب الأساسي', digits_compute=dp.get_precision('Payroll'))
    allowance_transport = fields.Float(string='بدل النقل', compute='_compute_amount', store=1, digits_compute=dp.get_precision('Payroll'))
    allowance_house = fields.Float(string='بدل سكن', compute='_compute_amount', store=1, digits_compute=dp.get_precision('Payroll'))
    allowance_ids = fields.One2many('hr.bonus.line', 'employee_id', string='البدلات', copy=True)

    @api.multi
    def get_reward_amount(self):
        '''احتساب مجموع  مكافآت‬ الموظف '''
        # TODO:
        return 0.0

    @api.multi
    def get_indemnity_amount(self):
        '''احتساب مجموع  تعويضات‬ الموظف '''
        # TODO:
        return 0.0

    @api.multi
    def get_deduction_amount(self):
        '''احتساب مجموع  حسميات الموظف '''
        # TODO:
        return 0.0

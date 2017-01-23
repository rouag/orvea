# -*- coding: utf-8 -*-

from openerp import api, fields, models, _
from openerp.exceptions import UserError


class WizardBonusEmployee(models.TransientModel):
    _name = 'wizard.bonus.employee'

    employee_ids = fields.Many2many('hr.employee', string=u'الموظفون')

    @api.multi
    def compute_employee(self):
        if not self.employee_ids:
            raise UserError(_(u"يجب عليك اختيار موظفون"))
        bonus_id = self._context.get('active_id', False)
        if bonus_id:
            bonus = self.env['hr.bonus'].browse(bonus_id)
            for employee in self.employee_ids:
                compute_method = False
                amount = percentage = 0.0
                if bonus.type == 'allowance':
                    compute_method = bonus.allowance_id.compute_method
                    amount = bonus.allowance_id.amount
                    percentage = bonus.allowance_id.percentage
                if bonus.type == 'reward':
                    compute_method = bonus.reward_id.compute_method
                    amount = bonus.reward_id.amount
                    percentage = bonus.reward_id.percentage
                if bonus.type == 'indemnity':
                    compute_method = bonus.indemnity_id.compute_method
                    amount = bonus.indemnity_id.amount
                    percentage = bonus.indemnity_id.percentage
                val = {
                    'bonus_id': bonus_id,
                    'employee_id': employee.id,
                    'number': employee.number,
                    'job_id': employee.job_id and employee.job_id.id or False,
                    'department_id': employee.department_id and employee.department_id.id or False,
                    'type': bonus.type,
                    'allowance_id': bonus.allowance_id and bonus.allowance_id.id or False,
                    'reward_id': bonus.reward_id and bonus.reward_id.id or False,
                    'indemnity_id': bonus.indemnity_id and bonus.indemnity_id.id or False,
                    'date_from': bonus.date_from,
                    'date_to': bonus.date_to,
                    'compute_method': compute_method,
                    'amount': amount,
                    'percentage': percentage}
                self.env['hr.bonus.line'].create(val)
        return {'type': 'ir.actions.act_window_close'}

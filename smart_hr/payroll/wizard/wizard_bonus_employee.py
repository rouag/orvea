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
                compute_method = bonus.compute_method
                amount = bonus.amount
                percentage = bonus.percentage
                name = ''
                if bonus.allowance_id:
                    name = bonus.allowance_id.name
                if bonus.reward_id:
                    name = bonus.reward_id.name
                if bonus.indemnity_id:
                    name = bonus.indemnity_id.name
                val = {
                    'name': name,
                    'bonus_id': bonus_id,
                    'employee_id': employee.id,
                    'number': employee.number,
                    'job_id': employee.job_id and employee.job_id.id or False,
                    'department_id': employee.department_id and employee.department_id.id or False,
                    'type': bonus.type,
                    'allowance_id': bonus.allowance_id and bonus.allowance_id.id or False,
                    'reward_id': bonus.reward_id and bonus.reward_id.id or False,
                    'indemnity_id': bonus.indemnity_id and bonus.indemnity_id.id or False,
                    'month_from': bonus.month_from,
                    'month_to': bonus.month_to,
                    'compute_method': compute_method,
                    'amount': amount,
                    'percentage': percentage,
                    'min_amount': bonus.min_amount}
                self.env['hr.bonus.line'].create(val)
        return {'type': 'ir.actions.act_window_close'}

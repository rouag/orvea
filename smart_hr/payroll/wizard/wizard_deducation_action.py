# -*- coding: utf-8 -*-

from openerp import api, fields, models, _


class WizardDeducationAction(models.TransientModel):
    _name = 'wizard.deducation.action'

    number_decision = fields.Char(string='رقم القرار')
    date_decision = fields.Date(string='تاريخ القرار')
    reason = fields.Text(string='السبب')

    @api.multi
    def action_exclusion(self):
        deduction_line_id = self._context.get('active_id', False)
        if deduction_line_id:
            deduction_line = self.env['hr.deduction.line'].browse(deduction_line_id)
            val = {
                'deduction_id': deduction_line.deduction_id.id,
                'employee_id': deduction_line.employee_id.id,
                'reason': self.reason,
                'number_decision': self.number_decision,
                'date_decision': self.date_decision,
                'action': u'إستبعاد موظف'
            }
            deduction_line.state = 'excluded'
            self.env['hr.deduction.history'].create(val)
        return {'type': 'ir.actions.act_window_close'}

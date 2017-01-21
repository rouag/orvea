# -*- coding: utf-8 -*-

from openerp import api, fields, models, _


class WizardBonusAction(models.TransientModel):
    _name = 'wizard.bonus.action'

    number_decision = fields.Char(string='رقم القرار')
    date_decision = fields.Date(string='تاريخ القرار')
    reason = fields.Text(string='السبب')

    @api.multi
    def action_start_stop(self):
        bonus_line_id = self._context.get('active_id', False)
        action = self._context.get('action', False)
        # TODO: l action est tpujours stop why ?
        print '--action-------', action
        if bonus_line_id:
            bonus_line = self.env['hr.bonus.line'].browse(bonus_line_id)
            val = {
                'bonus_id': bonus_line.bonus_id.id,
                'employee_id': bonus_line.employee_id.id,
                'reason': self.reason,
                'number_decision': self.number_decision,
                'date_decision': self.date_decision}
            if action == 'start':
                bonus_line.bonus_state = 'progress'
                val.update({'action': u'إعادة تفعيل'})
            elif action == 'stop':
                bonus_line.bonus_state = 'stop'
                val.update({'action': u'إيقاف'})
            self.env['hr.bonus.history'].create(val)
        return {'type': 'ir.actions.act_window_close'}

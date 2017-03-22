# -*- coding: utf-8 -*-

from openerp import fields, models, api

class hr_deprivation_cancel_wizard(models.TransientModel):
    _name = "hr.deprivation.cancel.wizard"
    _description = "Refuse Wizard"


    message = fields.Text(string = u'سبب الرفض')

    @api.multi
    def button_cancel(self):
        active_model = self._context.get('active_model', False)
        active_id = self._context.get('active_id', False)
        action = self._context.get('action', False)
        if active_model == 'hr.deprivation.premium.ligne' and active_id:
            sanction_line = self.env['hr.deprivation.premium.ligne'].browse(active_id)
            return sanction_line.button_cancel()
   
   
class hr_deprivation_confirm_wizard(models.TransientModel):
    _name = "hr.deprivation.confirm.wizard"
    _description = "Refuse Wizard"


    message = fields.Text(string = u'سبب الرفض')

    @api.multi
    def button_confirm(self):
        active_model = self._context.get('active_model', False)
        active_id = self._context.get('active_id', False)
        action = self._context.get('action', False)
        if active_model == 'hr.deprivation.premium.ligne' and active_id:
            sanction_line = self.env['hr.deprivation.premium.ligne'].browse(active_id)
            return sanction_line.button_confirm() 
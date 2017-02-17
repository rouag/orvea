# -*- coding: utf-8 -*-

from openerp import fields, models, api

class hr_cut_wizard(models.TransientModel):
    _name = "hr.cut.wizard"
    _description = "Refuse Wizard"

    message = fields.Text(string = u'سبب القطع')

    @api.multi
    def button_cut(self):
        # Variables
        cx = self.env.context or {}
        # Write refuse message
        for wiz in self:
            if wiz.message and cx.get('active_id', False) and cx.get('active_model', False):
                model_obj = self.env[cx.get('active_model')]
                rec_id = model_obj.browse(cx.get('active_id'))
                rec_id.message_post(u'سبب القطع: ' + unicode(wiz.message))
                return rec_id.sudo().button_cut()
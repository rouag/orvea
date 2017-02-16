# -*- coding: utf-8 -*-

from openerp import fields, models, api

class hr_refuse_wizard(models.TransientModel):
    _name = "hr.refuse.wizard"
    _description = "Refuse Wizard"

    message = fields.Text(string = u'سبب الرفض')

    @api.multi
    def button_refuse(self):
        # Variables
        cx = self.env.context or {}
        # Write refuse message
        for wiz in self:
            if wiz.message and cx.get('active_id', False) and cx.get('active_model', False):
                model_obj = self.env[cx.get('active_model')]
                rec_id = model_obj.browse(cx.get('active_id'))
                rec_id.message_post(u'سبب الرفض: ' + unicode(wiz.message))
                return rec_id.sudo().button_refuse()
            
class hr_refuse_wizard(models.TransientModel):
    _name = "hr.refuse.tarining.wizard"
    _description = "Refuse Wizard"

    message = fields.Text(string = u'سبب الرفض')
    
    @api.multi
    def button_refuse(self):
        # Variables
        cx = self.env.context or {}
        # Write refuse message
        for wiz  in self:
            if cx.get('active_id', False) and cx.get('active_model', False):
                model_obj = self.env[cx.get('active_model')]
                rec_id = model_obj.browse(cx.get('active_id'))
                return rec_id.sudo().action_refuse()
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
                return rec_id.button_refuse()

    @api.multi
    def button_refuse_waiting(self):
        # Variables
        cx = self.env.context or {}
        # Write refuse message
        for wiz in self:
            if wiz.message and cx.get('active_id', False) and cx.get('active_model', False):
                model_obj = self.env[cx.get('active_model')]
                rec_id = model_obj.browse(cx.get('active_id'))
                rec_id.message_post(u'سبب الرفض: ' + unicode(wiz.message))
                return rec_id.button_refuse_waiting()
            
class hr_tarining_refuse_wizard(models.TransientModel):
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
                rec_id.cause=self.message
                return rec_id.sudo().action_refuse()

class hr_create_employee_refuse_wizard(models.TransientModel):
    _name = "hr.employee.refuse.wizard"
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
                message = u" سبب الرفض:" + self.message
                rec_id.sudo().message_post(message)
                return rec_id.sudo().action_refuse()


class hr_deputation_refuse_wizard(models.TransientModel):
    _name = "hr.deputation.refuse.wizard"
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
                message = u" سبب الرفض:" + self.message
                rec_id.sudo().message_post(message)
                return rec_id.sudo().button_refuse_audit()
            
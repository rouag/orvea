# -*- coding: utf-8 -*-

from openerp import fields, models, api

class hr_refuse_appoint_wizard(models.TransientModel):
    _name = "hr.refuse.appoint.wizard"
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
                return rec_id.button_refuse_audit()
            
class hr_refuse_appoint1_wizard(models.TransientModel):
    _name = "hr.refuse.appoint1.wizard"
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
                return rec_id.button_refuse_audit()

class hr_refuse_appoint2_wizard(models.TransientModel):
    _name = "hr.refuse.appoint2.wizard"
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
                return rec_id.button_refuse_enterview_manager()


class hr_refuse_appoint3_wizard(models.TransientModel):
    _name = "hr.refuse.appoint3.wizard"
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
                return rec_id.button_refuse_recrutment_manager()

class hr_refuse_appoint4_wizard(models.TransientModel):
    _name = "hr.refuse.appoint4.wizard"
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
                return rec_id.button_refuse_recrutment_decider()

class hr_refuse_appoint5_wizard(models.TransientModel):
    _name = "hr.refuse.appoint5.wizard"
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
                return rec_id.button_refuse_direct()

class hr_refuse_appoint6_wizard(models.TransientModel):
    _name = "hr.refuse.appoint6.wizard"
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
                return rec_id.button_refuse_civil()


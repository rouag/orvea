# -*- coding: utf-8 -*-

from openerp import fields, models, api

class hr_refuse_increase_wizard(models.TransientModel):
    _name = "hr.refuse.increase.wizard"
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
                return rec_id.action_refuse_pim2()
            
class hr_refuse_increase_hrm_wizard(models.TransientModel):
    _name = "hr.refuse.increase.hrm.wizard"
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
                return rec_id.action_refuse_hrm()
class hr_refuse_increase_pim2_wizard(models.TransientModel):
    _name = "hr.refuse.increase.pim2.wizard"
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
                return rec_id.action_refuse_pim2()     
            
class hr_refuse_holidays1_wizard(models.TransientModel):
    _name = "hr.refuse.holidays1.wizard"
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
                return rec_id.button_delay_dm()

class hr_refuse_holidays2_wizard(models.TransientModel):
    _name = "hr.refuse.holidays2.wizard"
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
 
class hr_refuse_holidays3_wizard(models.TransientModel):
    _name = "hr.refuse.holidays3.wizard"
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
                return rec_id.button_refuse_external_audit()

class hr_refuse_holidays4_wizard(models.TransientModel):
    _name = "hr.refuse.holidays4.wizard"
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
                return rec_id.button_refuse_revision()
            
class hr_refuse_holidays5_wizard(models.TransientModel):
    _name = "hr.refuse.holidays5.wizard"
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
                return rec_id.button_refuse_revision_response()
            
            
            
            
class hr_refuse_holidays6_wizard(models.TransientModel):
    _name = "hr.refuse.holidays6.wizard"
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
                return rec_id.button_delay_hrm()
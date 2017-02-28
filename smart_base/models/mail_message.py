# -*- coding: utf-8 -*-


from openerp import models, fields, api
import os

class MailMessage(models.Model):
    _inherit = 'mail.message'

    ip_address = fields.Char(string=u'عنوان بروتوكول الإنترنت')
    mac_address = fields.Char(string=u'عنوان ماك')

    @api.model
    def create(self, vals):
        new_id = super(MailMessage, self).create(vals)
        print "mail message-----", new_id
        #print os.environ["REMOTE_ADDR"]
        return new_id

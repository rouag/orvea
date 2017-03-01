# -*- coding: utf-8 -*-


from openerp import models, fields, api
from subprocess import Popen, PIPE
import re
from openerp.http import request


class MailMessage(models.Model):
    _inherit = 'mail.message'

    ip_address = fields.Char(string=u'عنوان بروتوكول الإنترنت')
    mac_address = fields.Char(string=u'عنوان ماك')

    @api.model
    def create(self, vals):
        new_id = super(MailMessage, self).create(vals)
        IP = request.httprequest.environ['REMOTE_ADDR']
        if IP:
            new_id.write({'ip_address': IP})
            Popen(["ping", "-c 1", IP], stdout = PIPE)
            pid = Popen(["arp", "-n", IP], stdout = PIPE)
            s = pid.communicate()[0]
            if re.search(r"(([a-f\d]{1,2}\:){5}[a-f\d]{1,2})", s):
                mac = re.search(r"(([a-f\d]{1,2}\:){5}[a-f\d]{1,2})", s).groups()[0]
                new_id.write({'mac_address': mac})
        return new_id

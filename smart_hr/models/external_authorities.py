# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning


class ExternalAutorities(models.Model):
    _name = 'external.authorities'
    _description = u'الجهات الخارجية‬'
    name = fields.Char(string=u'المسمّى',required=True)
    holiday_status = fields.Many2one('hr.holidays.status', string='holiday status')
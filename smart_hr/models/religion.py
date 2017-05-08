# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning


class Religion(models.Model):
    _name = 'religion.religion'

    _description = u'الديانات'

    name = fields.Char(string=u'الإسم', required=1)
    code = fields.Char(string='الرمز')

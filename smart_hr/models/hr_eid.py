# -*- coding: utf-8 -*-

from openerp import fields, models, api, _
from openerp.exceptions import ValidationError

class hr_eid(models.Model):
    _name = 'hr.eid'
    _description = 'Eid'

    name = fields.Char(string=u'عيد / مناسبة', advanced_search=True)
    date_from = fields.Date(string=u'تاريخ من')
    date_to = fields.Date(string=u'تاريخ الى')
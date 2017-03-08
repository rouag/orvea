# -*- coding: utf-8 -*-

from openerp import fields, models, api, _
from openerp.exceptions import ValidationError


class res_city(models.Model):
    _name = 'res.city'
    _description = 'City'

    name = fields.Char(string=u'المسمّى', advanced_search=True)
    city_side = fields.Many2one('city.side', string=u'الجهة')
    code = fields.Char(string=u'الرمز')
    country_id = fields.Many2one('res.country',string=u'الدولة')

  

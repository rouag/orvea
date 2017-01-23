# -*- coding: utf-8 -*-
####################################
### This Module Created by smart-etech ###
####################################

from openerp import fields, models, api, _
from openerp.exceptions import ValidationError

class res_city(models.Model):
    _name = 'res.city'
    _description = 'City'

    name = fields.Char(string=u'المسمّى', advanced_search=True)
    days_before_after = fields.Integer(string=u'عدد أيام الأنتداب بقل و بعد التدريب', default=1, advanced_search=True)
    city_side = fields.Many2one('city.side',string = u'الجهة')
    
    
    @api.constrains('days_before_after')
    def _check_days(self):
        for rec in self:
            if rec.days_before_after < 0:
                raise ValidationError(u'عدد أيام الأنتداب بقل و بعد التدريب لا تكون بالسالب')
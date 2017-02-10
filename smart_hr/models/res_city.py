# -*- coding: utf-8 -*-

from openerp import fields, models, api, _
from openerp.exceptions import ValidationError


class res_city(models.Model):
    _name = 'res.city'
    _description = 'City'

    name = fields.Char(string=u'المسمّى', advanced_search=True)
    days_before_after = fields.Integer(string=u'عدد أيام الأنتداب بقل و بعد التدريب', default=1, advanced_search=True)
    city_side = fields.Many2one('city.side', string=u'الجهة')
    distance = fields.Float(string=u'المسافة')
    distance_ids = fields.Many2many('res.city', 'city_id_rel1', 'city_id_rel2', string=u'المسافات بين المدن')

    @api.constrains('days_before_after')
    def _check_days(self):
        for rec in self:
            if rec.days_before_after < 0:
                raise ValidationError(u'عدد أيام الأنتداب بقل و بعد التدريب لا تكون بالسالب')


# class res_city_distance(models.Model):
#     _name = 'res.city.distance'
#     _description = 'City'
# 
#     city_id = fields.Many2one(string=u'المدينة')
#     distance = fields.Float(string=u'المسافة')

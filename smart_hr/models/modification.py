# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from openerp.exceptions import Warning
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from datetime import date, datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class Contry(models.Model):
    _inherit = 'res.country'
    _description = u'البلدان'
   
    code=fields.Text(string='الرمز', )
    code_nat = fields.Text(string='الرمز', )
    
    national = fields.Char(string='الجنسية', )
   
class Region(models.Model):
     _inherit = 'city.side'
     _description = u'الجهات'
     contry = fields.Many2one('res.country', string='البلاد')
    


    
   
# -*- coding: utf-8 -*-

from openerp import fields, models, api, _
from openerp.exceptions import ValidationError
from lxml import etree

class hr_attendance(models.Model):
    _inherit = 'hr.attendance'
  

    id_emprinte = fields.Char(string=u'رقم ', advanced_search=True)
    mac_id = fields.Char(string=u'الآلة ', advanced_search=True)
   
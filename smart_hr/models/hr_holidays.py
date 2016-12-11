# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning

class HrHolidays(models.Model):
    _inherit = 'hr.holidays'  
    
    
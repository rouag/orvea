# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning

class Recruiters(models.Model):
    _name = 'recruiters.recruiters'  
    _description = u'جهات التوظيف' 
    name = fields.Char(string = u'الإسم', required=1)

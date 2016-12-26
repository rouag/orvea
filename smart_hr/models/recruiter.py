# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning

class Recruiter(models.Model):
    _name = 'recruiter.recruiter'  
    _description = u'جهات التوظيف' 
    
    name = fields.Char(string = u'الإسم', required=1)
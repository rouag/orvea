# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning

class Section(models.Model):
    _name = 'smart.section'  
    _description = u'الفرع' 
    
    name = fields.Char(string = u'الإسم', required=1)
    city = fields.Many2one('res.city',string = u'المدينة')
    recruiter = fields.Many2one('recruiter.recruiter',string = u'الجهة')

    @api.onchange('city')
    def _onchange_city(self):
        if self.city :
            self.recruiter = self.city.city_recruiter

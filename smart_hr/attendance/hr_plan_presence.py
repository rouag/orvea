# -*- coding: utf-8 -*-

from openerp import fields, models, api, _
from openerp.exceptions import ValidationError

class hr_plan_presence(models.Model):
    _name = "hr.plan.presence" 
    name = fields.Char(string=u'خطة الحضور والإنصراف', advanced_search=True)
    late = fields.Integer(string=u'تأخير بالدقائق',)
    percent_late = fields.Integer(string=u'ضارب تأخير ',)
    living_before_time = fields.Integer(string=u'الإنصراف المبكر بالدقائق',)
    percent_living = fields.Integer(string=u'ضارب الإنصراف المبكر  ',)
    max_sup_hour = fields.Integer(string=u' الحد الادنى للوقت الاضافي بالدقائق   ',)
    min_sup_hour = fields.Integer(string=u' الحد الأقصى للوقت الاضافي بالساعات   ',)
    
   
    
    
    
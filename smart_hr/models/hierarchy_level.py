# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning

class HierarchyLevel(models.Model):
    _name = 'hierarchy.level'  
    _description = u'مستوى العمق في ‫الهيكل‬' 
    
    department_id = fields.Many2one('hr.department',string = u'الإدارة',required=True)
    level = fields.Integer(string = u'العمق',required=True)
    
    _sql_constraints = [
        ('unique_department_id', 'UNIQUE(department_id)', u"لا يمكن اضافة اكثر من عمق لنفس الإدارة"),
    ]
    
    @api.multi
    def write(self, vals):
        if vals.get('level', False):
            self.department_id.level = vals.get('level', False)
        return super(HierarchyLevel, self).write(vals)
    
    @api.model
    def create(self, vals):
        res = super(HierarchyLevel, self).create(vals)
        res.department_id.level = res.level
        return res

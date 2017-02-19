# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning


class HierarchyLevel(models.Model):
    _name = 'hierarchy.level'
    _description = u'مستوى العمق في ‫الهيكل‬'
    _rec_name = 'department_type'

    department_type = fields.Many2one('hr.department.type', string=u'الإدارة نوع', required=True)
    level = fields.Integer(string=u'العمق', required=True)

    _sql_constraints = [
        ('unique_department_type', 'UNIQUE(department_type)', u"لا يمكن اضافة اكثر من عمق لنفس نوع الإدارة"),
    ]

    @api.multi
    def write(self, vals):
        if vals.get('level', False):
            self.department_type.level = vals.get('level', False)
        return super(HierarchyLevel, self).write(vals)

    @api.model
    def create(self, vals):
        res = super(HierarchyLevel, self).create(vals)
        res.department_type.level = res.level
        return res

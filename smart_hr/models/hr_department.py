# -*- coding: utf-8 -*-

from openerp import fields, models, api, _

class hr_department(models.Model):
    _inherit = 'hr.department'

    # Inherited Fields
    name = fields.Char(advanced_search=True)
    manager_id = fields.Many2one(advanced_search=True)
    parent_id = fields.Many2one(advanced_search=True)
    #
    is_root = fields.Boolean(string=u'قسم/إدارة رئيسية', default=True)

    @api.multi
    def write(self, vals):
        # Object
        emp_obj = self.env['hr.employee']
        # Update all employees in the same department
        if vals.get('manager_id', False):
            for rec in self:
                emp_ids = emp_obj.search([('department_id', '=', rec.id)])
                for emp in emp_ids:
                    if emp.id != vals['manager_id']:
                        emp.parent_id = vals['manager_id']
                    else:
                        emp.parent_id = rec.parent_id.manager_id
        return super(hr_department, self).write(vals)
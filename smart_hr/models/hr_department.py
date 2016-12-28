# -*- coding: utf-8 -*-

from openerp import fields, models, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning, ValidationError

class hr_department(models.Model):
    _inherit = 'hr.department'

    # Inherited Fields
    name = fields.Char(advanced_search=True,string=u'المسمّى')
    manager_id = fields.Many2one(advanced_search=True)
    parent_id = fields.Many2one(advanced_search=True,string=u'القسم الرئيسي')
    #
    is_root = fields.Boolean(string=u'قسم/إدارة رئيسية', default=True)
    dep_city = fields.Many2one('res.city',string = u'المدينة')
    dep_recruiter = fields.Many2one('recruiter.recruiter',string = u'الجهة')
    dep_section = fields.Many2one('smart.section',string = u'الفرع')
    level = fields.Integer(string = u'العمق')
    
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
    
    @api.onchange('dep_section')
    def _onchange_dep_section(self):
        if self.dep_section :
            self.dep_city = self.dep_section.city
            self.dep_recruiter = self.dep_section.city.city_recruiter
            
    @api.onchange('dep_city')
    def _onchange_dep_city(self):
        if self.dep_city :
            self.dep_recruiter = self.dep_city.city_recruiter

# compute level of department and his parent
    @api.onchange('parent_id')
    def _onchange_parent_id(self):
        if self.parent_id :
            if self.level<self.parent_id.level:
                warning = {
                    'title': _('Warning!'),
                    'message': _('the level of parent can not be lower than the level of child'),
                }
                return {'warning': warning}

            
            
            
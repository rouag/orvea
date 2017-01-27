# -*- coding: utf-8 -*-

from openerp import fields, models, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning, ValidationError

class hr_department(models.Model):
    _inherit = 'hr.department'

    # Inherited Fields
    name = fields.Char(advanced_search=True, string=u'المسمّى')
    manager_id = fields.Many2one(advanced_search=True)
    parent_id = fields.Many2one(advanced_search=True, string=u'الادارة الرئيسي')
    dep_city = fields.Many2one('res.city', string=u'المدينة')
    dep_Side = fields.Many2one('city.side', string=u'الجهة')
    code = fields.Char(string=u'الرمز')
    dep_type = fields.Many2one('hr.department.type', string=u'نوع الإدارة')

    
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


    @api.onchange('dep_city')
    def _onchange_dep_city(self):
        if self.dep_city :
            self.dep_Side = self.dep_city.city_side

# compute level of department and his parent
    @api.onchange('parent_id')
    def _onchange_parent_id(self):
        if self.parent_id:
            if self.dep_type.level < self.parent_id.dep_type.level:
                warning = {
                    'title': _('Warning!'),
                    'message': _(' الادارة مستوى الادارة الرئيسي لا يمكن أن يكون أقل من مستوى الطفل '),
                }
                return {'warning': warning}
            if self.dep_type.level > self.env.ref('smart_hr.data_hr_depatment_type_section').level:
                self.dep_city = self.parent_id.dep_city
                self.dep_Side = self.parent_id.dep_Side


class CitySide(models.Model):
    _name = 'city.side'
    _description = u'الجهة'
    
    name = fields.Char(advanced_search=True, string=u'المسمّى')
    
class HrDepartmentType(models.Model):
    
    _name = 'hr.department.type'
    _description = u'أنواع الإدارات'
    
    name = fields.Char(advanced_search=True, string=u'المسمّى')
    level = fields.Integer(string=u'العمق')


    
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
    dep_side = fields.Many2one('city.side', string=u'الجهة')
    code = fields.Char(string=u'الرمز')
    dep_type = fields.Many2one('hr.department.type', string=u'نوع الإدارة')

    @api.multi
    def name_get(self):
        res = []
        for dep in self:
            list_type = dep._context.get('list_type', False)
            if list_type and list_type == 'employee_form':
                # get the FAR3 of current department
                branche_dep_id = dep
                while branche_dep_id.parent_id and branche_dep_id.dep_type.level != 1:
                    branche_dep_id = dep.parent_id
                res.append((dep.id, "%s / %s" % (branche_dep_id.name or '', dep.name)))
            else:
                res.append((dep.id, "%s / %s" % (dep.parent_id.name or '', dep.name)))
        return res

    @api.multi
    def write(self,vals):
            return super(models.Model, self).write(vals)


    @api.onchange('dep_city')
    def _onchange_dep_city(self):
        if self.dep_city :
            self.dep_side = self.dep_city.city_side

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
                self.dep_side = self.parent_id.dep_side


class CitySide(models.Model):
    _name = 'city.side'
    _description = u'الجهة'
    
    name = fields.Char(advanced_search=True, string=u'المسمّى')
    code = fields.Char(string='الرمز')
    
    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = '[%s] %s' % (record.code, record.name)
            result.append((record.id, name))
        return result
    
class HrDepartmentType(models.Model):
    
    _name = 'hr.department.type'
    _description = u'أنواع الإدارات'
    
    name = fields.Char(advanced_search=True, string=u'المسمّى')
    level = fields.Integer(string=u'العمق')
    code = fields.Char(string='الرمز')
    
    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = '[%s] %s' % (record.code, record.name)
            result.append((record.id, name))
        return result

    
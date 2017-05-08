# -*- coding: utf-8 -*-

from openerp import fields, models, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning, ValidationError


class HrDepartment(models.Model):
    _inherit = 'hr.department'

    @api.one
    def _get_child_ids(self):
        # TODO: static method with 4 level must modify it to recursive
        all_childs = []
        for child in self.child_parent_ids:
            all_childs.append(child.id)
            all_childs += [x.id for x in child.child_parent_ids]
            for child2 in child.child_parent_ids:
                all_childs.append(child2.id)
                all_childs += [x.id for x in child2.child_parent_ids]
                for child3 in child2.child_parent_ids:
                    all_childs.append(child3.id)
                    all_childs += [x.id for x in child3.child_parent_ids]
        self.all_child_ids = list(set(all_childs))

    # Inherited Fields
    name = fields.Char(string=u'المسمّى')
    manager_id = fields.Many2one(string=u'مدير الادارة')
    parent_id = fields.Many2one(string=u'الادارة الرئيسي')
    dep_city = fields.Many2one('res.city', string=u'المدينة')
    dep_side = fields.Many2one('city.side', string=u'الجهة')
    code = fields.Char(string=u'الرمز')
    dep_type = fields.Many2one('hr.department.type', string=u'نوع الإدارة')
    child_parent_ids = fields.One2many('hr.department', 'parent_id', 'Children')
    all_child_ids = fields.Many2many('hr.department', compute=_get_child_ids, string="Child Departments")
    branch_id = fields.Many2one('hr.department', string=u'الفرع', compute="_compute_branch_id")

    def _compute_branch_id(self):
        for dep in self:
                # get the FAR3 of current department
            branche_dep_id = dep
            while branche_dep_id.parent_id and branche_dep_id.dep_type.level and branche_dep_id.dep_type.level != 1:
                branche_dep_id = branche_dep_id.parent_id
            dep.branch_id = branche_dep_id.id

    @api.multi
    def name_get(self):
        if u'list_type' in self._context:
            return getattr(self, self._context[u'list_type'])()
        else:
            return super(HrDepartment, self).name_get()

    def _get_dep_name_employee_form(self):
        res = []
        for dep in self:
                # get the FAR3 of current department
            branche_dep_id = dep
            while branche_dep_id.parent_id and branche_dep_id.dep_type.level and branche_dep_id.dep_type.level != 1:
                branche_dep_id = branche_dep_id.parent_id
            if branche_dep_id.id != dep.id:
                res.append((dep.id, "%s / %s" % (branche_dep_id.name or '', dep.name)))
            else:
                res.append((dep.id, "%s / %s" % (dep.parent_id.name or '', dep.name)))
        return res

    @api.multi
    def write(self, vals):
        return super(models.Model, self).write(vals)

    @api.onchange('dep_city')
    def _onchange_dep_city(self):
        if self.dep_city:
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

    @api.multi
    def button_child_ids(self):
        chid_ids = self.all_child_ids.ids
        value = {
                'name': u'‫الإدارات',
                'view_type': 'form',
                'view_mode': 'kanban,form,tree',
                'res_model': 'hr.department',
                'view_id': False,
                'type': 'ir.actions.act_window',
                'domain': [('id','in', chid_ids)]
            }
        return value

class CitySide(models.Model):
    _name = 'city.side'
    _description = u'الجهة'

    name = fields.Char(string=u'المسمّى')
    code = fields.Char(string='الرمز')
    allowance_ids = fields.Many2many('hr.allowance.type', string=u'بدلات مناطق الجبلية أو النائية')


class HrDepartmentType(models.Model):
    _name = 'hr.department.type'
    _description = u'أنواع الإدارات'

    name = fields.Char(string=u'المسمّى', required=1)
    level = fields.Integer(string=u'العمق')
    code = fields.Char(string='الرمز')


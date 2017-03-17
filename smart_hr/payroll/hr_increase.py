# -*- coding: utf-8 -*-

from openerp import models, api, fields, _
from openerp.exceptions import ValidationError
from datetime import date, datetime, timedelta
from openerp.addons.smart_base.util.umalqurra import *
from umalqurra.hijri_date import HijriDate
from umalqurra.hijri import Umalqurra


class hrIncrease(models.Model):
    _name = 'hr.increase'
    _inherit = ['mail.thread']
    _order = 'id desc'
    _description = u'العلاوة'

    @api.multi
    def get_default_date(self):
        # get end date of month 01 
        date = get_hijri_month_end(HijriDate, Umalqurra, '01')
        if fields.date.today() > date:
            raise ValidationError(u"لا يمكن إنشاء علاوات بعد نهاية شهر محرّم! ")
        else:
            return fields.date.today()

    name = fields.Char(string=' المسمى', readonly=1, states={'new': [('readonly', 0)]})
    number_decision = fields.Char(string='رقم القرار', required=1,states={'new': [('readonly', 0)]})
    date_decision = fields.Date(string=' تاريخ القرار', required=1,states={'new': [('readonly', 0)]})
    date = fields.Date(string='تاريخ الطلب', readonly=1, default=get_default_date)
    employee_deprivated_ids = fields.One2many('hr.employee.deprivation', 'increase_id', string=u'الموظفين المستثنين من العلاوة', required=1)
    state = fields.Selection([('draft', u'طلب'),
                              ('pim', u'المصاقة على الموظفين المستثنين من العلاوة '),
                              ('hrm', u'مدير شؤون الموظفين'),
                              ('pim2', u'المصاقة على نسب العلاوة '),
                              ('done', u'اعتمدت'),
                              ], string='الحالة', readonly=1, default='draft')
    note = fields.Text(string='ملاحظات')
    department_level1_id = fields.Many2one('hr.department', string='الفرع', readonly=1, states={'draft': [('readonly', 0)]})
    department_level2_id = fields.Many2one('hr.department', string='القسم', readonly=1, states={'draft': [('readonly', 0)]})
    department_level3_id = fields.Many2one('hr.department', string='الشعبة', readonly=1, states={'draft': [('readonly', 0)]})
    salary_grid_type_id = fields.Many2one('salary.grid.type', string='الصنف', readonly=1, states={'draft': [('readonly', 0)]},)
    

    @api.model
    def create(self, vals):
        res = super(hrIncrease, self).create(vals)
        # Sequence
        vals = {}
        vals['name'] = self.env['ir.sequence'].get('hr.increase.seq')
        res.write(vals)
        return res

    @api.one
    def action_pim(self):
        self.state = 'pim'

    @api.one
    def button_refuse(self):
        self.state = 'draft'

    @api.one
    def action_refuse_pim2(self):
        self.state = 'hrm'

    @api.one
    def action_hrm(self):
        self.state = 'hrm'

    @api.one
    def action_pim2(self):
        self.state = 'pim2'

    @api.one
    def action_done(self):
        self.state = 'done'


class HrEmployeeDeprivation(models.Model):
    _name = 'hr.employee.deprivation'

    increase_id = fields.Many2one('hr.increase')
    employee_id = fields.Many2one('hr.employee', string=u'الموظف', required=1)
    reason = fields.Char(string=u'السبب', required=1)
    department_level1_id = fields.Many2one('hr.department', related='increase_id.department_level1_id')
    department_level2_id = fields.Many2one('hr.department', related='increase_id.department_level2_id')
    department_level3_id = fields.Many2one('hr.department', related='increase_id.department_level3_id')
    salary_grid_type_id = fields.Many2one('salary.grid.type', related='increase_id.salary_grid_type_id')

    @api.onchange('department_level1_id', 'department_level2_id', 'department_level3_id', 'salary_grid_type_id')
    def onchange_department_level(self):
        dapartment_obj = self.env['hr.department']
        employee_obj = self.env['hr.employee']
        department_level1_id = self.increase_id.department_level1_id and self.increase_id.department_level1_id.id or False
        department_level2_id = self.increase_id.department_level2_id and self.increase_id.department_level2_id.id or False
        department_level3_id = self.increase_id.department_level3_id and self.increase_id.department_level3_id.id or False
        employee_ids = []
        dapartment_id = False
        if department_level3_id:
            dapartment_id = department_level3_id
        elif department_level2_id:
            dapartment_id = department_level2_id
        elif department_level1_id:
            dapartment_id = department_level1_id
        if dapartment_id:
            dapartment = dapartment_obj.browse(dapartment_id)
            employee_ids += [x.id for x in dapartment.member_ids]
            for child in dapartment.all_child_ids:
                employee_ids += [x.id for x in child.member_ids]
        result = {}
        if not employee_ids:
            # get all employee
            employee_ids = employee_obj.search([('employee_state', '=', 'employee')]).ids
        # filter by type
        if self.salary_grid_type_id:
            employee_ids = employee_obj.search([('id', 'in', employee_ids), ('type_id', '=', self.increase_id.salary_grid_type_id.id)]).ids
        result.update({'domain': {'employee_id': [('id', 'in', list(set(employee_ids)))]}})
        return result


class hrEmployeeIncreasePercent(models.Model):

    _name = 'hr.employee.increase.percent'
    _inherit = ['mail.thread']
    _order = 'id desc'

    _description = u'نسبة العلاوة'
    increase_id  = fields.Many2one('hr.increase')
    employee_id = fields.Many2one('hr.employee', string=u'الموظف', required=1, readonly=1)
    increase_percent = fields.Float(string=u'نسبة العلاوة', required=1)

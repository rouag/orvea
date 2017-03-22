# -*- coding: utf-8 -*-

from openerp import models, api, fields, _
from openerp.exceptions import ValidationError
from openerp.exceptions import UserError
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
#         if fields.date.today() > date:
#             raise ValidationError(u"لا يمكن إنشاء علاوات بعد نهاية شهر محرّم! ")
#         else:
#             return fields.date.today()

    name = fields.Char(string=' المسمى', readonly=1, states={'new': [('readonly', 0)]})
    number_decision = fields.Char(string='رقم القرار', required=1,states={'new': [('readonly', 0)]})
    date_decision = fields.Date(string=' تاريخ القرار', required=1,states={'new': [('readonly', 0)]})
    date = fields.Date(string='تاريخ الطلب', readonly=1, default=get_default_date)
    employee_deprivated_ids = fields.One2many('hr.employee.deprivation', 'increase_id', string=u'الموظفين المستثنين من العلاوة', required=1)
    employee_increase_ids = fields.One2many('hr.employee.increase.percent', 'increase_id', string=u'الموظفين المستحقين للعلاوة  ', required=1)
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
        for rec in self :
            for line in rec.employee_deprivated_ids :
                increase_ids = self.env['hr.employee.increase.percent'].search([('employee_id', '=', line.id)])
                if increase_ids :
                     raise UserError(u"يجب إنشاء حساب بنكي للإيداع  للموظف  %s " % line.display_name)
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

    @api.multi
    def action_done(self):
        for rec in self :
            for line in rec.employee_increase_ids: 
                employee_increase_obj = self.env['employee.increase']
                self.env['employee.increase'].create({'name': rec.date,
                                                      'amount': line.increase_percent,
                                                      'date': self.date,
                                                      'employee_id': line.employee_id.id,
                                                  })
        self.state = 'done'


class HrEmployeeDeprivation(models.Model):
    _name = 'hr.employee.deprivation'

    increase_id = fields.Many2one('hr.increase')
    employee_id = fields.Many2one('hr.employee', string=u'الموظف', required=1)
    reason = fields.Char(string=u'السبب', readonly=1 ,compute='_compute_raison' )
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
        result = []
        result_sanction = []
        res = {}
        # filter by type
        if self.salary_grid_type_id:
            employee_ids = employee_obj.search([('id', 'in', employee_ids), ('type_id', '=', self.increase_id.salary_grid_type_id.id)]).ids
        result = list(set(employee_ids))
        liste_employee_ids = set()
        sanctions = self.env['hr.sanction.ligne'].search([('state', '=', 'done'), ('sanction_id.type_sanction', '=', self.env.ref('smart_hr.data_hr_sanction_type_grade').id)])
        for rec in sanctions:
            liste_employee_ids.add(rec.employee_id.id)
        result_sanction = list(liste_employee_ids)
        result_inter = []
        for e in result:
            if e in result_sanction:
                result_inter.append(e)
        res['domain'] = {'employee_id': [('id', 'in', list(result_inter))]}
        return res

    @api.multi
    @api.depends('employee_id')
    def _compute_raison(self):
        for rec in self:
            sanctions = self.env['hr.sanction.ligne'].search([('state', '=', 'done'),('employee_id','=',rec.employee_id.id), ('sanction_id.type_sanction', '=', self.env.ref('smart_hr.data_hr_sanction_type_grade').id)],limit=1)
            if sanctions:
                rec.reason = sanctions.raison

class hrEmployeeIncreasePercent(models.Model):

    _name = 'hr.employee.increase.percent'
    _inherit = ['mail.thread']
    _order = 'id desc'

    _description = u'نسبة العلاوة'
    increase_id  = fields.Many2one('hr.increase')
    employee_id = fields.Many2one('hr.employee', string='الموظفين', required=1)
   # employee_id = fields.Many2one('hr.employee', string=u'الموظف', required=1)
    increase_percent = fields.Float(string=u'المبلغ', required=1, compute='increase_percent_count')
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
        filte_empl = []
        result_total = []
        if self.salary_grid_type_id:
            employee_ids = employee_obj.search([('id', 'in', employee_ids), ('type_id', '=', self.increase_id.salary_grid_type_id.id)]).ids
              # filter by type
        filte_empl = list(set(employee_ids))

        liste_employee_ids = set()
        sanctions = self.env['hr.sanction.ligne'].search([('state', '=', 'done'), ('sanction_id.type_sanction', '=', self.env.ref('smart_hr.data_hr_sanction_type_grade').id)])
        for rec in sanctions:
            liste_employee_ids.add(rec.employee_id.id)
        result_sanction = list(liste_employee_ids)
        result_total = set(filte_empl) - set(result_sanction)
        result.update({'domain': {'employee_id': [('id', 'in',list(result_total))]}})
        return result

    @api.multi
    @api.depends('employee_id')
    def increase_percent_count(self):
        for rec in self:
            increase_ids = self.env['salary.grid.detail'].search([('type_id', '=', rec.employee_id.type_id.id), ('degree_id', '=', rec.employee_id.degree_id.id),
                                                               ('grade_id', '=', rec.employee_id.grade_id.id) ],limit=1)
            if increase_ids:
                rec.increase_percent = increase_ids.increase 
            else:
                rec.increase_percent = 0

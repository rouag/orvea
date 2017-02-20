# -*- coding: utf-8 -*-

from openerp import models, api, fields, _
from openerp.exceptions import ValidationError
from datetime import date, datetime, timedelta


class hrIncrease(models.Model):

    _name = 'hr.increase'
    _inherit = ['mail.thread']
    _order = 'id desc'
    _description = u'العلاوة'

    name = fields.Char(string=' المسمى', readonly=1, states={'new': [('readonly', 0)]})
    number_decision = fields.Char(string='رقم القرار', required=1,states={'new': [('readonly', 0)]})
    date_decision = fields.Date(string=' تاريخ القرار', required=1,states={'new': [('readonly', 0)]})
    date = fields.Date(string='تاريخ الطلب', readonly=1, default=fields.Datetime.now())
    employee_deprivated_ids = fields.Many2many('hr.employee', string=u'الموظفين المستثنين من العلاوة', required=1)
    employee_beneficiaries_ids = fields.One2many('hr.employee.increase.percent','increase_id', string=u'الموظفين المستحقين للعلاوة')
    reasons = fields.Char(string='الاسباب', required=1)
    increase_id = fields.Many2one('hr.increase.type', string='العلاوة', required=1)
    state = fields.Selection([('draft', u'طلب'),
                              ('pim', u'المصاقة على الموظفين المستثنين من العلاوة '),
                              ('hrm', u'مدير شؤون الموظفين'),
                              ('pim2', u'المصاقة على نسب العلاوة '),
                              ('done', u'اعتمدت'),
                              ], string='الحالة', readonly=1, default='draft')
    note = fields.Text(string='ملاحظات')

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
    def action_refuse(self):
        self.state = 'draft'
        
    @api.one
    def action_refuse_pim2(self):
        self.state = 'hrm'

    @api.one
    def action_hrm(self):
        employee_deprivated_ids = self.employee_deprivated_ids.ids
        employee_beneficiaries_ids = []
        for employee in self.env['hr.employee'].search([('id', 'not in', employee_deprivated_ids), ('type_id.name', '!=', self.env.ref('smart_hr.data_salary_grid_type6').id)]):
            employee_beneficiaries = self.env['hr.employee.increase.percent'].create({'employee_id': employee.id,'increase_percent': 0, 'increase_id': self.id})

        self.state = 'hrm'

    @api.one
    def action_pim2(self):
        self.state = 'pim2'

    @api.one
    def action_done(self):
        self.state = 'done'


class hrEmployeeIncreasePercent(models.Model):

    _name = 'hr.employee.increase.percent'
    _inherit = ['mail.thread']
    _order = 'id desc'

    _description = u'نسبة العلاوة'
    increase_id  = fields.Many2one('hr.increase')
    employee_id = fields.Many2one('hr.employee', string=u'الموظف', required=1, readonly=1)
    increase_percent = fields.Float(string=u'نسبة العلاوة', required=1)

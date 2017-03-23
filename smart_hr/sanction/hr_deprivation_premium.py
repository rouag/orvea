# -*- coding: utf-8 -*-

from openerp import models, fields, api


class HrDeprivationPremium(models.Model):
    _name = 'hr.deprivation.premium'
    _inherit = ['mail.thread']
    _order = 'id desc'
    _description = u'قرار حرمان من العلاوة'

    name = fields.Char(string='رقم القرار', required=1, readonly=1, states={'draft': [('readonly', 0)]})
    order_date = fields.Date(string='تاريخ القرار', default=fields.Datetime.now())
    deprivation_file = fields.Binary(string='ملف القرار', states={'draft': [('readonly', 0)]})
    date_deprivation = fields.Date(string='التاريخ' , default=fields.Datetime.now(), states={'draft': [('readonly', 0)]})
    deprivation_file_name = fields.Char(string='ملف القرار')
    deprivation_ids = fields.One2many('hr.deprivation.premium.ligne', 'deprivation_id',
                                      string=u'قائمة المحرومين من العلاوة', readonly=1,
                                      states={'draft': [('readonly', 0)]})
    state = fields.Selection([('draft', '  طلب'),
                              ('waiting', u'في إنتظار الاعتماد'),
                              ('done', u'اعتمدت'),
                              ('refused', u'مرفوضة'),
                              ], string='الحالة', readonly=1, default='draft')

    @api.multi
    def action_draft(self):
        for deprivation in self:
            deprivation.state = 'waiting'

    @api.multi
    def button_refuse(self):
        for deprivation in self:
            deprivation.state = 'refused'

    @api.multi
    def action_waiting(self):
        for deprivation in self:
            deprivation.state = 'done'


class HrdeprivationPremiumLigne(models.Model):
    _name = 'hr.deprivation.premium.ligne'
    _description = u' قائمة المحرومين من العلاوة'

    deprivation_id = fields.Many2one('hr.deprivation.premium', string=' قائمة المحرومين من العلاوة', ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string=u'  الموظف', required=1)
    raison = fields.Char(string='السبب', readonly=1,  compute='_compute_raison' )
    state = fields.Selection([('waiting', 'في إنتظار التاكيد'),
                              ('excluded', 'مستبعد'),
                              ('done', 'تم التاكيد'),
                              ], string='الحالة', readonly=1, default='waiting')




    @api.onchange('employee_id')
    def onchange_employee_id(self):
        res = {}
        employee_ids = set()
        sanctions = self.env['hr.sanction.ligne'].search([('state', '=', 'done'), ('sanction_id.type_sanction', '=', self.env.ref('smart_hr.data_hr_sanction_type_grade').id)])
        for rec in sanctions:
            employee_ids.add(rec.employee_id.id)
        res['domain'] = {'employee_id': [('id', 'in', list(employee_ids))]}
        return res

    @api.multi
    @api.depends('employee_id')
    def _compute_raison(self):
        for rec in self:
            sanctions = self.env['hr.sanction.ligne'].search([('state', '=', 'done'),('employee_id','=',rec.employee_id.id), ('sanction_id.type_sanction', '=', self.env.ref('smart_hr.data_hr_sanction_type_grade').id)],limit=1)
            if sanctions:
                rec.raison = sanctions.raison

    @api.multi
    def button_cancel(self):
        for deprivation in self:
            deprivation.state = 'excluded'
    
    @api.multi
    def button_confirm(self):
        for deprivation in self:
            deprivation.state = 'done'
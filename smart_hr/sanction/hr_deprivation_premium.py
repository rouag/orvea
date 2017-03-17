# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from openerp.exceptions import Warning
from openerp.exceptions import ValidationError
from openerp.exceptions import UserError
from datetime import date, datetime, timedelta


class hrdeprivationPremium(models.Model):
    _name = 'hr.deprivation.premium'
    _inherit = ['mail.thread']
    _order = 'id desc'
    _description = u'قرار حرمان من العلاوة'

    name = fields.Char(string='رقم القرار', required=1, readonly=1, states={'draft': [('readonly', 0)]})
    order_date = fields.Date(string='تاريخ القرار', default=fields.Datetime.now(), readonly=1)
    deprivation_text = fields.Html(string='نص القرار')
    deprivation_ids = fields.One2many('hr.deprivation.premium.ligne', 'deprivation_id', string=u'قائمة المحرومين من العلاوة', readonly=1, states={'draft': [('readonly', 0)]})
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
            deprivation.state = 'extern'


class HrdeprivationPremiumLigne(models.Model):
    _name = 'hr.deprivation.premium.ligne'
    _description = u' قائمة المحرومين من العلاوة'

    deprivation_id = fields.Many2one('hr.deprivation.premium', string=' قائمة المحرومين من العلاوة', ondelete='cascade')
    employee_id = fields.Many2one('hr.employee', string=u'  الموظف', required=1)
    raison = fields.Char(string='السبب ')
    state = fields.Selection([('waiting', 'في إنتظار التاكيد'),
                              ('excluded', 'مستبعد'),
                              ('done', 'تم التاكيد'),
                           ], string='الحالة', readonly=1, default='waiting')


#     @api.onchange('employee_id')
#     def onchange_employee_id(self):
#       
#             employee_ids = []
#             for rec in self.env['hr.sanction.ligne'].search([('employee_id','=',self.employee_id.id),('state', '=','done'),('sanction_id.type_sanction','=',self.env.ref('smart_hr.data_hr_sanction_type_grade').id)]):
#                 employee_ids.append(rec.id)
#                 print"employee_ids",employee_ids
#             res['domain'] = {'employee_id': [('id', 'in', employee_ids)]}
#             return res
          
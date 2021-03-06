# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from openerp.exceptions import except_orm, Warning, RedirectWarning


class ResPartner(models.Model):
    _inherit = 'res.partner'

    company_type = fields.Selection(
        [('person', u'شخص'),
         ('hospital', u'مستشفى'),
         ('governmental_entity', u'جهة حكومية'),
         ('company', u'شركة'),
         ('faculty', u'جامعة'),
         ('school', u'معهد'),
         ('inter_reg_org',u'منظمة دولية أو اقليمية'),
         ])
    is_hospital = fields.Boolean(string='is hospital')
   # inter_reg_org = fields.Boolean(string=u'منظمة دولية أو اقليمية', default=False)
    insurance = fields.Boolean(string=u'تابعة للتأمين', default=False)
    hospital_director = fields.Char(string=u'مدير المستشفى')
    code = fields.Char(string=u'الرمز')
    @api.multi
    def on_change_company_type(self, company_type):
        if company_type == 'hospital':
            company_type = 'company'
            return {'value': {'is_company': company_type == 'company', 'is_hospital': True}}
        else:
            return {'value': {'is_company': company_type == 'company', 'is_hospital': False}}


class ResPartnerBank(models.Model):
    _inherit = 'res.partner.bank'

    account_opening_date = fields.Date(string=u'تاريخ فتح الحساب')
    is_deposit = fields.Boolean(string='للإيداع')
    employee_id = fields.Many2one('hr.employee', string=u'الموظف')
    type_bank = fields.Selection(
        [
            ('governmental_entity', u' حكومية'),
            ('private', u'أهلي'),
        ])

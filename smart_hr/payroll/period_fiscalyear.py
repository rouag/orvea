# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp.addons.smart_base.util.umalqurra import *
from openerp import models, api, fields, _


class AccountFiscalyear(models.Model):
    _name = "account.fiscalyear"
    _description = "السنة المالية"
    _order = "date_start, id"

    code = fields.Char(string='الرمز', size=6, required=True)
    name = fields.Char(string='السنة المالية', required=True)
    date_start = fields.Date(string=u'تاريخ البدء', required=True)
    date_stop = fields.Date(string=u'تاريخ الانتهاء', required=True)
    period_ids = fields.One2many('account.period', 'fiscalyear_id', string=u'الفترات')
    company_id = fields.Many2one('res.company', string=u'شركة', required=True, default=lambda self: self.env['res.users'].search([('id', '=', self._uid)]).company_id.id)

    @api.multi
    def create_period(self):
        period_obj = self.env['account.period']
        for fy in self:
            ds = datetime.strptime(fy.date_start, '%Y-%m-%d')
            ihijri_month = 0
            while ds.strftime('%Y-%m-%d') < fy.date_stop:
                de = ds + relativedelta(months=1, days=-2)
                ihijri_month += 1
                if ihijri_month < 10:
                    month_name = '0' + str(ihijri_month)
                else:
                    month_name = str(ihijri_month)

                if de.strftime('%Y-%m-%d') > fy.date_stop:
                    de = datetime.strptime(fy.date_stop, '%Y-%m-%d')

                period_obj.create({
                    'name': month_name,
                    'code': ds.strftime('%m/%Y'),
                    'date_start': ds.strftime('%Y-%m-%d'),
                    'date_stop': de.strftime('%Y-%m-%d'),
                    'fiscalyear_id': fy.id,
                })
                ds = ds + relativedelta(months=1)
        return True


class AccountPeriod(models.Model):
    _name = 'account.period'
    _order = "date_start"
    _rec_name = 'name'

    _description = "فترة الحساب"
    name = fields.Selection(MONTHS, 'اسم الفترة', required=True)
    code = fields.Char('الشفرة', size=12)
    date_start = fields.Date('بداية الفترة', required=True)
    date_stop = fields.Date('نهاية الفترة', required=True)
    fiscalyear_id = fields.Many2one('account.fiscalyear', 'السنة المالية', required=True, select=True)
    company_id = fields.Many2one('res.company', related='fiscalyear_id.company_id', string='شركة', store=True, readonly=True)
    is_open = fields.Boolean('مفتوحة', default=True)
    _sql_constraints = [
        ('name_company_uniq', 'unique(name, company_id)', 'يجب أن يكون اسم الفترة فريدة من نوعها لكل شركة!'),
    ]

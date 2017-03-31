# -*- coding: utf-8 -*-
from datetime import datetime
from dateutil.relativedelta import relativedelta
from openerp import models, api, fields, _
from openerp.addons.smart_base.util.umalqurra import *
from umalqurra.hijri_date import HijriDate
from umalqurra.hijri import Umalqurra


class HrFiscalyear(models.Model):
    _name = "hr.fiscalyear"
    _description = "السنة "
    _order = "date_start, id"

    code = fields.Char(string='الرمز', size=6, required=True)
    name = fields.Char(string='السنة ', required=True)
    date_start = fields.Date(string=u'تاريخ البدء', required=True)
    date_stop = fields.Date(string=u'تاريخ الانتهاء', required=True)
    period_ids = fields.One2many('hr.period', 'fiscalyear_id', string=u'الفترات')
    company_id = fields.Many2one('res.company', string=u'شركة', required=True, default=lambda self: self.env['res.users'].search([('id', '=', self._uid)]).company_id.id)

    @api.multi
    def create_period(self):
        period_obj = self.env['hr.period']
        for fy in self:
            ds = datetime.strptime(fy.date_start, '%Y-%m-%d')
            while ds.strftime('%Y-%m-%d') < fy.date_stop:
                hijri_month = get_hijri_month_by_date(HijriDate, Umalqurra, ds)
                hijri_year = get_hijri_year_by_date(HijriDate, Umalqurra, ds)
                month_name = MONTHS[hijri_month] + '/' + str(hijri_year)
                date_start = get_hijri_month_start_by_year(HijriDate, Umalqurra, hijri_year, hijri_month)
                date_stop = get_hijri_month_end__by_year(HijriDate, Umalqurra, hijri_year, hijri_month)
                period_obj.create({
                    'name': month_name,
                    'code': str(hijri_month) + '/' + str(hijri_year),
                    'date_start': date_start,
                    'date_stop': date_stop,
                    'fiscalyear_id': fy.id,
                })
                ds = ds + relativedelta(months=1)
        return True


class HrPeriod(models.Model):
    _name = 'hr.period'
    _order = "date_start"
    _rec_name = 'name'

    _description = "فترة الحساب"
    name = fields.Char('اسم الفترة', required=True)
    code = fields.Char('الشفرة', size=12)
    date_start = fields.Date('بداية الفترة', required=True)
    date_stop = fields.Date('نهاية الفترة', required=True)
    fiscalyear_id = fields.Many2one('hr.fiscalyear', 'السنة ', required=True, select=True)
    company_id = fields.Many2one('res.company', related='fiscalyear_id.company_id', string='شركة', store=True, readonly=True)
    is_open = fields.Boolean('مفتوحة', default=True)
    _sql_constraints = [
        ('name_company_uniq', 'unique(name, company_id)', 'يجب أن يكون اسم الفترة فريدة من نوعها!'),
    ]

    @api.multi
    def button_open_period(self):
        self.ensure_one()
        self.is_open = True

    @api.multi
    def button_close_period(self):
        self.ensure_one()
        self.is_open = False


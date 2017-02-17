# -*- coding: utf-8 -*-

from openerp import models, api, fields, _
from openerp.exceptions import ValidationError
from dateutil import relativedelta
import time as time_date
from datetime import datetime
from openerp.addons.smart_base.util.time_util import days_between

MONTHS = [('01', 'محرّم'),
          ('02', 'صفر'),
          ('03', 'ربيع الأول'),
          ('04', 'ربيع الثاني'),
          ('05', 'جمادي الأولى'),
          ('06', 'جمادي الآخرة'),
          ('07', 'رجب'),
          ('08', 'شعبان'),
          ('09', 'رمضان'),
          ('10', 'شوال'),
          ('11', 'ذو القعدة'),
          ('12', 'ذو الحجة')]


class hrDifference(models.Model):
    _name = 'hr.difference'
    _inherit = ['mail.thread']
    _order = 'id desc'
    _description = u'الفروقات'

    name = fields.Char(string=' المسمى', required=1, readonly=1, states={'new': [('readonly', 0)]})
    # TODO: get default MONTH
    month = fields.Selection(MONTHS, string='الشهر', required=1, readonly=1, states={'new': [('readonly', 0)]})
    date = fields.Date(string='تاريخ الإنشاء', required=1, default=fields.Datetime.now(), readonly=1, states={'new': [('readonly', 0)]})
    date_from = fields.Date('تاريخ من', default=lambda *a: time_date.strftime('%Y-%m-01'),
                            readonly=1, states={'new': [('readonly', 0)]})
    date_to = fields.Date('إلى', default=lambda *a: str(datetime.now() + relativedelta.relativedelta(months=+1, day=1, days=-1))[:10],
                          readonly=1, states={'new': [('readonly', 0)]})
    state = fields.Selection([('new', 'مسودة'),
                              ('waiting', 'في إنتظار الإعتماد'),
                              ('cancel', 'مرفوض'),
                              ('done', 'اعتمدت')], string='الحالة', readonly=1, default='new')
    line_ids = fields.One2many('hr.difference.line', 'difference_id', string='الفروقات', readonly=1, states={'new': [('readonly', 0)]})

    @api.onchange('month')
    def onchange_month(self):
        if self.month:
            self.name = u'فروقات شهر %s' % self.month
            line_ids = []
            # TODO: must update date_from and date_to
            # delete current line
            self.line_ids.unlink()
            # فروقات خارج الدوام
            line_ids += self.get_difference_overtime()
            # فروقات الأنتداب
            line_ids += self.get_difference_deputation()
            # فروقات النقل
            line_ids += self.get_difference_transfert()
            #
            self.line_ids = line_ids

    @api.one
    def action_waiting(self):
        self.state = 'waiting'

    @api.multi
    def action_done(self):
        self.state = 'done'

    @api.one
    def action_refuse(self):
        self.state = 'cancel'

    @api.multi
    def get_difference_transfert(self):
        self.ensure_one()
        line_ids = []
        hr_setting = self.env['hr.setting'].search([], limit=1)
        if hr_setting:
            transfert_ids = self.env['hr.employee.transfert'].search([('create_date', '>=', self.date_from),
                                                                      ('create_date', '<=', self.date_to),
                                                                      ('state', '=', 'done')])
            for transfert in transfert_ids:
                # 1- بدل طبيعة العمل
                amount = (hr_setting.allowance_proportion * transfert.employee_id.wage)
                if amount > 0:
                    amount = amount / 100
                vals = {'difference_id': self.id,
                        'name': hr_setting.allowance_job_nature.name,
                        'employee_id': transfert.employee_id.id,
                        'number_of_days': 0,
                        'number_of_hours': 0.0,
                        'amount': amount,
                        'type': 'transfert'}
                line_ids.append(vals)

                # 2- بدل إنتداب
                amount = (hr_setting.deputation_days * (transfert.employee_id.wage / 22))
                if amount > 0:
                    amount = amount / 100
                vals = {'difference_id': self.id,
                        'name': hr_setting.allowance_deputation.name,
                        'employee_id': transfert.employee_id.id,
                        'number_of_days': hr_setting.deputation_days,
                        'number_of_hours': 0.0,
                        'amount': amount,
                        'type': 'transfert'}
                line_ids.append(vals)
                # 3- بدل ترحيل
                amount = (hr_setting.deportation_amount)
                vals = {'difference_id': self.id,
                        'name': hr_setting.allowance_deportation.name,
                        'employee_id': transfert.employee_id.id,
                        'number_of_days': 0,
                        'number_of_hours': 0.0,
                        'amount': amount,
                        'type': 'transfert'}
                line_ids.append(vals)
                # 4- نسبة الراتب
                amount = ((100 - hr_setting.salary_proportion) * transfert.employee_id.wage) / 100
                vals = {'difference_id': self.id,
                        'name': u'نسبة الراتب',
                        'employee_id': transfert.employee_id.id,
                        'number_of_days': 0,
                        'number_of_hours': 0.0,
                        'amount': amount,
                        'type': 'transfert'}
                line_ids.append(vals)
        return line_ids


class hrDifferenceLine(models.Model):
    _name = 'hr.difference.line'

    difference_id = fields.Many2one('hr.difference', string=' الفروقات', ondelete='cascade')
    name = fields.Char(string=' المسمى', required=1)
    employee_id = fields.Many2one('hr.employee', string='الموظف', required=1)
    job_id = fields.Many2one(related='employee_id.job_id', store=True, readonly=True, string=' الوظيفة')
    department_id = fields.Many2one(related='employee_id.department_id', store=True, readonly=True, string=' الادارة')
    amount = fields.Float(string='المبلغ')
    number_of_days = fields.Float(string='عدد الأيام')
    number_of_hours = fields.Float(string='عدد الساعات')
    month = fields.Selection(MONTHS, related='difference_id.month', store=True, readonly=True, string='الشهر')
    # TODO: do the store for state
    state = fields.Selection(related='difference_id.state', string='الحالة')
    # TODO: , النقل توظيف
    type = fields.Selection([('increase', 'علاوة'),
                             ('promotion', 'ترقية'),
                             ('scholarship', 'ابتعاث'),
                             ('appoint', 'تعيين'),
                             ('lend', 'إعارة'),
                             ('commissioning', 'تكليف'),
                             ('deputation', 'إنتداب'),
                             ('overtime', 'خارج الدوام'),
                             ('transfert', 'نقل'),
                             ('training', 'تدريب')], string='النوع', readonly=1)

# -*- coding: utf-8 -*-

from openerp import models, api, fields, _
from openerp.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from umalqurra.hijri_date import HijriDate

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


class hrLoan(models.Model):
    _name = 'hr.loan'
    _inherit = ['mail.thread']
    _description = u'القرض'
    _order = 'id desc'

    # TODO: refaire les actions apres la modification des lifges par month

    @api.one
    @api.depends('line_ids', 'amount')
    def _compute_residual_amount(self):
        residual_amount = self.amount
        for line in self.line_ids:
            residual_amount -= line.amount
        self.residual_amount = residual_amount

    name = fields.Char(string='رقم القرض', required=1, readonly=1, states={'new': [('readonly', 0)]})
    employee_id = fields.Many2one('hr.employee', string='الموظف', required=1)
    number = fields.Char(related='employee_id.number', store=True, readonly=True, string=' الرقم الوظيفي')
    job_id = fields.Many2one(related='employee_id.job_id', store=True, readonly=True, string=' الوظيفة')
    department_id = fields.Many2one(related='employee_id.department_id', store=True, readonly=True, string=' الادارة')
    loan_type_id = fields.Many2one('hr.loan.type', string='نوع القرض', required=1)
    date = fields.Date('تاريخ الطلب', default=lambda *a: fields.Datetime.now(), readonly=1, states={'new': [('readonly', 0)]})
    date_from = fields.Date('تاريخ بداية الخصم', readonly=1, states={'new': [('readonly', 0)]})
    date_to = fields.Date('القسط الأخير', readonly=1, states={'new': [('readonly', 0)]})
    installment_number = fields.Integer(string='عدد الأقساط', required=1)
    amount = fields.Float(string='مبلغ القرض', required=1)
    monthly_amount = fields.Float(string='قيمة القسط الشهري', required=1)
    residual_amount = fields.Float(string='المبلغ المتبقي', compute='_compute_residual_amount', store=1)
    bank_id = fields.Many2one('res.bank', string='البنك', required=1)
    number_decision = fields.Char(string='رقم القرار', required=1, readonly=1, states={'new': [('readonly', 0)]})
    date_decision = fields.Date(string=' تاريخ القرار', required=1, readonly=1, states={'new': [('readonly', 0)]})
    note = fields.Text(string='ملاحظات')
    payment_full_amount = fields.Boolean(string='سداد كامل المبلغ')
    state = fields.Selection([('new', 'طلب'),
                              ('waiting', 'في إنتظار الإعتماد'),
                              ('cancel', 'مرفوض'),
                              ('progress', 'ساري'),
                              ('done', 'منتهي')
                              ], string='الحالة', readonly=1, default='new')
    line_ids = fields.One2many('hr.loan.line', 'loan_id', string='سجل الأقساط', readonly=1)
    history_ids = fields.One2many('hr.loan.history', 'loan_id', string='سجل العمليات', readonly=1)

    @api.onchange('date_from', 'amount', 'monthly_amount')
    def _onchange_date(self):
        if self.date_from and self.amount and self.monthly_amount:
            number = self.amount / (self.monthly_amount or 1.0)
            installment_number = int(number)
            if number > installment_number:
                installment_number += 1
            self.installment_number = installment_number
            # TODO: review the * 30
            self.date_to = fields.Date.from_string(self.date_from) + relativedelta(days=installment_number * 30)
            # get lines
            dt = fields.Date.from_string(self.date_from)
            months = []
            while dt < fields.Date.from_string(self.date_to):
                um = HijriDate()
                dates = str(dt).split('-')
                um.set_date_from_gr(int(dates[0]), int(dates[1]), int(dates[2]))
                month_val = {'loan_id': self.id,
                             'amount': self.monthly_amount,
                             'month': str(int(um.month)).zfill(2)
                             }
                months.append(month_val)
                dt = fields.Date.from_string(str(dt)) + relativedelta(days=30)
            self.line_ids = months

    @api.one
    def copy(self, default=None):
        default = dict(default or {})
        default.update(payment_full_amount=False)
        return super(hrLoan, self).copy(default)

    @api.one
    def action_waiting(self):
        self.state = 'waiting'

    @api.one
    def action_refuse(self):
        self.state = 'cancel'

    @api.multi
    def action_progress(self):
        self.state = 'progress'

    @api.one
    def action_done(self):
        self.state = 'done'


class hrLoanLine(models.Model):
    _name = 'hr.loan.line'

    loan_id = fields.Many2one('hr.loan', string='القرض')
    employee_id = fields.Many2one(related='loan_id.employee_id', store=True, readonly=True, string='الموظف')
    job_id = fields.Many2one(related='loan_id.employee_id.job_id', store=True, readonly=True, string=' الوظيفة')
    department_id = fields.Many2one(related='loan_id.employee_id.department_id', store=True, readonly=True, string=' الادارة')
    amount = fields.Float(string='قيمة القسط', required=1)
    date = fields.Date('تاريخ الحسم', required=False)
    month = fields.Selection(MONTHS, string='الشهر')


class hrLoanHistory(models.Model):
    _name = 'hr.loan.history'

    loan_id = fields.Many2one('hr.loan', string='القرض')
    action = fields.Char(string='الإجراء')
    reason = fields.Char(string='السبب')
    month = fields.Selection(MONTHS, string='الشهر')
    number_decision = fields.Char(string='رقم القرار')
    date_decision = fields.Date(string='تاريخ القرار')


class hrLoanType(models.Model):
    _name = 'hr.loan.type'
    _description = u'نوع القرض'

    name = fields.Char(string=' الوصف', required=1)
    code = fields.Char(string='الرمز', required=1)

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = '[%s] %s' % (record.code, record.name)
            result.append((record.id, name))
        return result

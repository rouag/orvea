# -*- coding: utf-8 -*-

from openerp import models, api, fields, _
from openerp.exceptions import ValidationError
from dateutil.relativedelta import relativedelta
from umalqurra.hijri_date import HijriDate
from openerp.exceptions import UserError
from datetime import datetime
from openerp.addons.smart_base.util.umalqurra import *


class HrLoan(models.Model):
    _name = 'hr.loan'
    _inherit = ['mail.thread']
    _description = u'القرض'
    _order = 'id desc'

    # TODO: refaire les actions apres la modification des lifges par month
    # TODO: il faut ajouter l annee par exemple pour un loan sur deux annees

    @api.one
    @api.depends('line_ids.date', 'amount', 'state')
    def _compute_residual_amount(self):
        residual_amount = self.amount
        for line in self.line_ids:
            if line.state=="done":
                residual_amount -= line.amount
        self.residual_amount = residual_amount

    name = fields.Char(string='رقم القرض', required=1, readonly=1, states={'new': [('readonly', 0)]})
    employee_id = fields.Many2one('hr.employee', string='الموظف', required=1, readonly=1, states={'new': [('readonly', 0)]})
    number = fields.Char(related='employee_id.number', store=True, readonly=True, string=' رقم الوظيفة')
    job_id = fields.Many2one(related='employee_id.job_id', store=True, readonly=True, string=' الوظيفة')
    department_id = fields.Many2one(related='employee_id.department_id', store=True, readonly=True, string=' الادارة')
    loan_type_id = fields.Many2one('hr.loan.type', string='نوع القرض', required=1, readonly=1, states={'new': [('readonly', 0)]})
    date = fields.Date('تاريخ القرض', default=lambda *a: fields.Datetime.now(), readonly=1, states={'new': [('readonly', 0)]})
    date_from = fields.Date('تاريخ بداية الخصم', readonly=1, states={'new': [('readonly', 0)]})
    date_to = fields.Date('تاريخ نهاية الخصم', readonly=1, states={'new': [('readonly', 0)]})
    installment_number = fields.Integer(string='عدد الأقساط', required=1, readonly=1, states={'new': [('readonly', 0)]})
    amount = fields.Float(string='مبلغ القرض', required=1, readonly=1, states={'new': [('readonly', 0)]})
    monthly_amount = fields.Float(string='قيمة القسط', required=1, readonly=1, states={'new': [('readonly', 0)]})
    residual_amount = fields.Float(string='المبلغ المتبقي', compute='_compute_residual_amount', store=1)
    bank_id = fields.Many2one('res.bank', string='جهة القرض', required=1, readonly=1, states={'new': [('readonly', 0)]})
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
    deputation_id = fields.Many2one('hr.deputation', string='الانتداب')
    is_deputation_advance = fields.Boolean(string='سلفة عن بدل انتداب', related='loan_type_id.is_deputation_advance')

    @api.constrains('amount')
    @api.onchange('amount')
    def _onchange_amount(self):
        if self. amount and self.loan_type_id.is_deputation_advance and self.deputation_id:
            deputation_amount, transport_amount, deputation_allowance = self.deputation_id.get_deputation_allowance_amount(self.department_id.duration)
            if self.amount > deputation_amount:
                warning = {
                    'title': _('تحذير!'),
                    'message': _('لا يمكن للسلفة ان تتجاوز بدل الانتداب!'),
                }
                return {'warning': warning}

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
                             'month': str(int(um.month)).zfill(2),
                             'state': 'progress'
                             }
                months.append(month_val)
                dt = fields.Date.from_string(str(dt)) + relativedelta(days=30)
            self.line_ids = months

    @api.one
    def copy(self, default=None):
        default = dict(default or {})
        default.update(payment_full_amount=False)
        return super(HrLoan, self).copy(default)

    @api.multi
    def unlink(self):
        for loan in self:
            if loan.state != 'new':
                raise UserError(_(u'لا يمكن حذف قرض  إلا في حالة طلب !'))
        return super(HrLoan, self).unlink()

    @api.one
    def action_waiting(self):
        self.state = 'waiting'

    @api.one
    def button_refuse(self):
        self.state = 'cancel'

    @api.multi
    def action_progress(self):
        self.state = 'progress'

    @api.one
    def action_done(self):
        self.state = 'done'

    @api.multi
    def get_loan_employee_month(self, month, employee_id):
        # search all loan for this employee
        loans = self.search([('employee_id', '=', employee_id), ('state', '=', 'progress')])
        res = []
        for loan in loans:
            # إذا تم تجاوز هذا الشهر  لا يؤخذ بعين الإعتبار لأنه تم حذفه وتعويضه بشهر أخر
            # إذا تم سداد كامل المبلغ يجب أن يؤخذ باقي المبلغ
            if loan.payment_full_amount:
                res.append({'name': u'سداد كامل المبلغ  القرض رقم %s' % loan.name, 'amount': loan.residual_amount})
            else:
                # just add amount for current month
                lines = loan.line_ids.search([('month', '=', month)])
                if lines:
                    res.append({'name': u'قرض  رقم : %s' % loan.name, 'amount': lines[0].amount})
        return res

    @api.multi
    def update_loan_date(self, month, employee_id):
        # search all loan for this employee
        loans = self.search([('employee_id', '=', employee_id), ('state', '=', 'progress')])
        for loan in loans:
            # إذا تم سداد كامل المبلغ يجب أن يتم تعديل التاريخ في كل الأشهر
            if loan.payment_full_amount:
                loan.line_ids.write({'date': datetime.now().date(), 'state': 'done'})
            # else just update date for current month
            else:
                lines = loan.line_ids.search([('month', '=', month)])
                lines.write({'date': datetime.now().date(), 'state': 'done'})
            # if residual_amount = 0 make this loan as done
            if loan.residual_amount == 0.0:
                loan.state = 'done'


class HrLoanLine(models.Model):
    _name = 'hr.loan.line'

    loan_id = fields.Many2one('hr.loan', string='القرض', ondelete='cascade')
    employee_id = fields.Many2one(related='loan_id.employee_id', store=True, readonly=True, string='الموظف')
    job_id = fields.Many2one(related='loan_id.employee_id.job_id', store=True, readonly=True, string=' الوظيفة')
    department_id = fields.Many2one(related='loan_id.employee_id.department_id', store=True, readonly=True, string=' الادارة')
    amount = fields.Float(string='قيمة القسط', required=1)
    date = fields.Date('تاريخ الحسم', required=False)
    month = fields.Selection(MONTHS, string='الشهر')
    state = fields.Selection([('progress', ' غير مسدد'),
                              ('done', ' مسدد'),
                              ], string='الحالة', readonly=1, default='progress')


class HrLoanHistory(models.Model):
    _name = 'hr.loan.history'

    loan_id = fields.Many2one('hr.loan', string='القرض', ondelete='cascade')
    action = fields.Selection([('across', 'تجاوز شهر'), ('full_amount', 'سداد كامل المبلغ')], string='الإجراء')
    reason = fields.Char(string='السبب')
    month = fields.Selection(MONTHS, string='الشهر')
    number_decision = fields.Char(string='رقم القرار')
    date_decision = fields.Date(string='تاريخ القرار')


class HrLoanType(models.Model):
    _name = 'hr.loan.type'
    _description = u'نوع القرض'

    name = fields.Char(string=' الوصف', required=1)
    code = fields.Char(string='الرمز', required=1)
    is_deputation_advance = fields.Boolean(string='سلفة عن بدل انتداب')
    
    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = '[%s] %s' % (record.code, record.name)
            result.append((record.id, name))
        return result

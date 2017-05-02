# -*- coding: utf-8 -*-

from openerp import models, api, fields, _
from openerp.addons.smart_base.util.umalqurra import *


class HrPayrollSettlement(models.Model):
    _name = 'hr.payroll.settlement'
    _inherit = ['mail.thread']
    _order = 'id desc'
    _description = u'التسوية'
    _rec_name = 'employee_id'

    date = fields.Date(string='تاريخ التسوية', readonly=1, default=fields.Datetime.now())
    period_id = fields.Many2one('hr.period', string=u'مخصص لفترة', required=1, readonly=1, states={'new': [('readonly', 0)]})
    number_decision = fields.Char(string='رقم القرار', readonly=1, states={'new': [('readonly', 0)]})
    date_decision = fields.Date(string=' تاريخ القرار', readonly=1, states={'new': [('readonly', 0)]})
    employee_id = fields.Many2one('hr.employee', string='الموظف', required=1, readonly=1,
                                  states={'new': [('readonly', 0)]})
    type = fields.Selection([('deduction', 'حسم'),
                             ('addition', 'اضافة')], string='حسم / اضافة', required=1, readonly=1,
                            states={'new': [('readonly', 0)]})
    compute_method = fields.Selection([('amount_salary', 'مبلغ على الراتب الأساسي'),
                                       ('amount_allowance', 'مبلغ على بدل'),
                                       ('days_absence', 'عدد أيام غياب'),
                                       ('days_delay', 'عدد أيام تأخير')], string='طريقة الإحتساب', required=1,
                                      readonly=1, states={'new': [('readonly', 0)]})
    amount = fields.Float(string='المبلغ', readonly=1, states={'new': [('readonly', 0)]})
    days = fields.Float(string='عدد الأيام', readonly=1, states={'new': [('readonly', 0)]})
    allowance_id = fields.Many2one('hr.allowance.type', string='البدل', readonly=1, states={'new': [('readonly', 0)]})
    note = fields.Text(string='ملاحظات', readonly=1, states={'new': [('readonly', 0)]})
    state = fields.Selection([('new', 'إعداد'),
                              ('done', 'اعتمدت'),
                              ('cancel', 'ملغى')], string='الحالة', default='new', readonly=1)

    @api.one
    def action_done(self):
        self.state = 'done'

    @api.one
    def action_cancel(self):
        self.state = 'cancel'

    @api.multi
    def get_settlement_by_period(self, period_id, employee_id, allowance_total):
        settlements = self.search(
            [('employee_id', '=', employee_id), ('state', '=', 'done'), ('period_id', '=', period_id)])
        employee = self.env['hr.employee'].browse(employee_id)
        res = []
        grid_id, basic_salary = employee.get_salary_grid_id(False)
        if not grid_id:
            return []
        for settlement in settlements:
            factor = 1.0
            settlement_type = u'اضافة'
            if settlement.type == 'deduction':
                factor = -1.0
                settlement_type = u'حسم'

            if settlement.compute_method == 'amount_salary':
                amount = settlement.amount * factor
                vals = {'name': u'تسوية %s : مبلغ على الراتب الأساسي' % settlement_type,
                        'employee_id': employee_id,
                        'number_of_days': 0.0,
                        'number_of_hours': 0.0,
                        'amount': amount,
                        'category': 'difference',
                        'type': 'settlement'}
                res.append(vals)
            elif settlement.compute_method == 'amount_allowance':
                amount = settlement.amount * factor
                vals = {'name': u'تسوية %s : مبلغ على  %s' % (settlement_type, settlement.allowance_id.name),
                        'employee_id': employee_id,
                        'number_of_days': 0.0,
                        'number_of_hours': 0.0,
                        'amount': amount,
                        'category': 'difference',
                        'type': 'settlement'}
                res.append(vals)
            elif settlement.compute_method == 'days_absence':
                # حسم‬  الغياب‬ يكون‬ من‬  جميع البدلات  و  الراتب‬ الأساسي
                amount = (basic_salary + allowance_total) / 30.0 * settlement.days * factor
                vals = {'name': u'تسوية %s : غياب بدون عذر' % settlement_type,
                        'employee_id': employee_id,
                        'number_of_days': settlement.days,
                        'number_of_hours': 0.0,
                        'amount': amount,
                        'category': 'difference',
                        'type': 'settlement'}
                res.append(vals)
                retirement_amount = -1.0 * basic_salary * grid_id.retirement / 100.0 / 30.0 * settlement.days * factor
                if retirement_amount:
                    vals = {'name': u'تسوية %s : تقاعد غياب بدون عذر' % settlement_type,
                            'employee_id': employee_id,
                            'number_of_days': settlement.days,
                            'number_of_hours': 0.0,
                            'amount': retirement_amount,
                            'category': 'difference',
                            'type': 'settlement'}
                    res.append(vals)
            elif settlement.compute_method == 'days_delay':
                #  حسم‬  التأخير يكون‬ من‬  الراتب‬ الأساسي فقط
                amount = basic_salary / 30.0 * settlement.days * factor
                vals = {'name': u'تسوية %s : تأخير و خروج مبكر' % settlement_type,
                        'employee_id': employee_id,
                        'number_of_days': settlement.days,
                        'number_of_hours': 0.0,
                        'amount': amount,
                        'category': 'difference',
                        'type': 'settlement'}
                res.append(vals)
        return res

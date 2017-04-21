# -*- coding: utf-8 -*-

from openerp import api, fields, models, _
from openerp.exceptions import UserError
from openerp.addons.smart_base.util.umalqurra import *
from umalqurra.hijri_date import HijriDate
from umalqurra.hijri import Umalqurra
from dateutil.relativedelta import relativedelta


class WizardLoanAction(models.TransientModel):
    _name = 'wizard.loan.action'

    period_id = fields.Many2one('hr.period', string=u'الفترة', domain=[('is_open', '=', True)], required=1)
    number_decision = fields.Char(string='رقم القرار')
    date_decision = fields.Date(string='تاريخ القرار')
    reason = fields.Text(string='السبب')

    @api.model
    def default_get(self, fields):
        res = super(WizardLoanAction, self).default_get(fields)
        loan_id = self._context.get('active_id', False)
        loan_line_obj = self.env['hr.loan.line']
        loan_lines = loan_line_obj.search([('loan_id', '=', loan_id), ('state', '=', 'progress')])
        if loan_lines:
            date_start = loan_lines[0].date_start
            date_stop = loan_lines[0].date_stop
            # get period_id for specific month
            period_id = self.env['hr.period'].search([('date_start', '>=', date_start),
                                                      ('date_stop', '<=', date_stop),
                                                      ], limit=1
                                                     )
            if period_id:
                res.update({'period_id': period_id.id})
        else:
            raise UserError(_(u'إنتهى القرض  لا يوجد شهر يمكن تجاوزه.'))
        return res

    @api.multi
    def action_across_month(self):
        loan_id = self._context.get('active_id', False)
        loan_obj = self.env['hr.loan']
        loan_line_obj = self.env['hr.loan.line']
        action = self._context.get('action', False)
        dt = fields.Date.from_string(self.period_id.date_start)
        day = dt.day
        if loan_id:
            if action == 'across':  # تجاوز شهر
                # must delete this month add another month
                loan_lines = loan_line_obj.search([('loan_id', '=', loan_id), ('date_start', '=', self.period_id.date_start), ('date_stop', '=', self.period_id.date_stop)])
                loan_lines.unlink()
                um = HijriDate()
                loan = loan_obj.search([('id', '=', loan_id)])
                last_date_start = fields.Date.from_string(loan.line_ids[-1].date_start)
                last_date_stop = fields.Date.from_string(loan.line_ids[-1].date_stop)
                temp_date_start = last_date_stop + relativedelta(days=1)
                hijri_month = get_hijri_month_by_date(HijriDate, Umalqurra, temp_date_start)
                hijri_year = get_hijri_year_by_date(HijriDate, Umalqurra, temp_date_start)
                new_date_start = get_hijri_month_start_by_year(HijriDate, Umalqurra, hijri_year, hijri_month)
                new_date_stop = get_hijri_month_end__by_year(HijriDate, Umalqurra, hijri_year, hijri_month)
                dates = str(new_date_start).split('-')
                um.set_date_from_gr(int(dates[0]), int(dates[1]), day)
                new_line_val = {'loan_id': loan_id,
                                'amount': loan.monthly_amount,
                                'date_start': new_date_start,
                                'date_stop': new_date_stop,
                                'name': MONTHS[int(um.month)] + '/' + str(int(um.year)),
                                }
                loan_line_obj.create(new_line_val)
            val = {
                'loan_id': loan_id,
                'reason': self.reason,
                'period_id': self.period_id.id,
                'number_decision': self.number_decision,
                'date_decision': self.date_decision,
                'action': action,
            }
            if action == 'full_amount':
                self.env['hr.loan'].browse(loan_id).payment_full_amount = True
            self.env['hr.loan.history'].create(val)
        return {'type': 'ir.actions.act_window_close'}

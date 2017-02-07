# -*- coding: utf-8 -*-

from openerp import api, fields, models, _
from openerp.exceptions import UserError

# TODO: move MONTHS to smart_base and get it here and all another file
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


class WizardLoanAction(models.TransientModel):
    _name = 'wizard.loan.action'

    month = fields.Selection(MONTHS, string='الشهر', required=1)
    number_decision = fields.Char(string='رقم القرار')
    date_decision = fields.Date(string='تاريخ القرار')
    reason = fields.Text(string='السبب')

    @api.model
    def default_get(self, fields):
        res = super(WizardLoanAction, self).default_get(fields)
        loan_id = self._context.get('active_id', False)
        loan_line_obj = self.env['hr.loan.line']
        loan_lines = loan_line_obj.search([('loan_id', '=', loan_id), ('date', '=', False)])
        if loan_lines:
            res.update({'month': loan_lines[0].month})
        else:
            raise UserError(_(u'إنتهى القرض  لا يوجد شهر يمكن تجاوزه.'))
        return res

    @api.multi
    def action_across_month(self):
        loan_id = self._context.get('active_id', False)
        loan_obj = self.env['hr.loan']
        loan_line_obj = self.env['hr.loan.line']
        action = self._context.get('action', False)
        if loan_id:
            if action == 'across':  # تجاوز شهر
                # must delete this month add another month
                loan_lines = loan_line_obj.search([('loan_id', '=', loan_id), ('month', '=', self.month)])
                loan_lines.unlink()
                # create new month
                loan = loan_obj.search([('id', '=', loan_id)])
                last_month = loan.line_ids[-1].month
                new_month = int(last_month) + 1
                new_line_val = {'loan_id': loan_id,
                                'amount': loan.monthly_amount,
                                'month': str(int(new_month)).zfill(2)
                                }
                loan_line_obj.create(new_line_val)
            val = {
                'loan_id': loan_id,
                'reason': self.reason,
                'month': self.month,
                'number_decision': self.number_decision,
                'date_decision': self.date_decision,
                'action': action,
            }
            if action == 'full_amount':
                self.env['hr.loan'].browse(loan_id).payment_full_amount = True
            self.env['hr.loan.history'].create(val)
        return {'type': 'ir.actions.act_window_close'}

# -*- coding: utf-8 -*-

from openerp import api, fields, models, _

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

    @api.multi
    def action_across_month(self):
        loan_id = self._context.get('active_id', False)
        action = self._context.get('action', False)
        if loan_id:
            val = {
                'loan_id': loan_id,
                'reason': self.reason,
                'month': self.month,
                'number_decision': self.number_decision,
                'date_decision': self.date_decision,
            }
            if action == 'across':
                val.update({'action': u'تجاوز شهر'})
            elif action == 'full_amount':
                val.update({'action': u'سداد كامل المبلغ'})
                self.env['hr.loan'].browse(loan_id).payment_full_amount = True
            self.env['hr.loan.history'].create(val)
        return {'type': 'ir.actions.act_window_close'}

# -*- coding: utf-8 -*-

from openerp import api, fields, models


class WizardJobUpdate(models.TransientModel):
    _name = 'wizard.job.update'

    update_request_id = fields.Many2one('hr.job.update', string=u'طلب التحوير', domain=[('state', '=', 'done')])
    decision_number = fields.Char(related="update_request_id.decision_number", readonly=1, string=u'رقم القرار')
    decision_date = fields.Date(related="update_request_id.decision_date", readonly=1, string=u'تاريخ القرار')
    report_type = fields.Selection([('requested', u'الجارية'),
                                    ('accepted', u'الموافق عليها'),
                                    ], string=u'طلبات التحوير', default='requested')

    @api.multi
    def print_report(self):
        report_action = self.env['report'].get_action(self, 'smart_hr.report_job_update')
        data = {'ids': [], 'form': self.read([])[0]}
        report_action['data'] = data
        return report_action

# -*- coding: utf-8 -*-

from openerp import api, fields, models


class WizardJobDescription(models.TransientModel):
    _name = 'wizard.job.description'

    job_id = fields.Many2one('hr.job', string=u'الوظيفة')

    @api.multi
    def print_report(self):
        report_action = self.env['report'].get_action(self, 'smart_hr.report_job_description')
        data = {'ids': [], 'form': self.read([])[0]}
        report_action['data'] = data
        return report_action

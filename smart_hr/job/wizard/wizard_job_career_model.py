# -*- coding: utf-8 -*-

from openerp import api, fields, models


class WizardJobCareerModel(models.TransientModel):
    _name = 'wizard.job.career.model'

    job_id = fields.Many2one('hr.job', string=u'الوظيفة', required=1)

    @api.multi
    def print_report(self):
        report_action = self.env['report'].get_action(self, 'smart_hr.report_job_career_model')
        data = {'ids': [], 'form': self.read([])[0]}
        report_action['data'] = data
        return report_action

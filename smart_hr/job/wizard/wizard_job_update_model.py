# -*- coding: utf-8 -*-

from openerp import api, fields, models


class WizardJobUpdateModel(models.TransientModel):
    _name = 'wizard.job.update.model'

    job_update_id = fields.Many2one('hr.job.update', string=u'طلب التحوير', required=1)
    job_id = fields.Many2one('hr.job', string=u'الوظيفة', required=1)

    @api.onchange('job_update_id')
    def _onchange_job_update_id(self):
        res = {}
        if self.job_update_id:
            job_ids = [rec.job_id.id for rec in self.job_update_id.job_update_ids]
            res['domain'] = {'job_id': [('id', 'in', job_ids)]}
            return res
        # return empty job list
        res['domain'] = {'job_id': [('id', '=', -1)]}
        return res

    @api.multi
    def print_report(self):
        report_action = self.env['report'].get_action(self, 'smart_hr.report_job_update_model')
        data = {'ids': [], 'form': self.read([])[0]}
        report_action['data'] = data
        return report_action

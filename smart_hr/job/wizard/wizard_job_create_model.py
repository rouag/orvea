# -*- coding: utf-8 -*-

from openerp import api, fields, models


class WizardJobCreateModel(models.TransientModel):
    _name = 'wizard.job.create.model'

    job_create_id = fields.Many2one('hr.job.create', string=u'طلب إحداث وظيفة', domain=[('state', '!=', 'done')], required=1)
    job_create_line_id = fields.Many2one('hr.job.create.line', string=u'الوظيفة', required=1)

    @api.onchange('job_create_id')
    def _onchange_job_create_id(self):
        res = {}
        if self.job_create_id:
            job_create_line_ids = [rec.id for rec in self.job_create_id.line_ids]
            print job_create_line_ids
            res['domain'] = {'job_create_line_id': [('id', 'in', job_create_line_ids)]}
            return res
        # return empty job list
        res['domain'] = {'job_create_line_id': [('id', '=', -1)]}
        return res

    @api.multi
    def print_report(self):
        report_action = self.env['report'].get_action(self, 'smart_hr.report_job_create_model')
        data = {'ids': [], 'form': self.read([])[0]}
        report_action['data'] = data
        return report_action

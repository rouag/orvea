# -*- coding: utf-8 -*-

from openerp import api, fields, models


class WizardJobScaleDownModel(models.TransientModel):
    _name = 'wizard.job.scale.down.model'

    line_id = fields.Many2one('hr.job.move.grade.line', string=u'الوظيفة', required=1)
    job_id = fields.Many2one('hr.job', related='line_id.job_id', string=u'الوظيفة', required=1)

    @api.onchange('job_id')
    def _onchange_job_id(self):
        res = {}
        job_ids = []
        if not self.job_id:
            move_ids = self.env['hr.job.move.grade'].search([('move_type', '=', 'scale_down'), ('state', '!=', 'done')])
            if move_ids:
                for rec in move_ids:
                    job_ids += [line.job_id.id for line in rec.job_movement_ids]
                print job_ids
                res['domain'] = {'job_id': [('id', 'in', job_ids)]}
                return res
            # return empty job list
            res['domain'] = {'job_id': [('id', '=', -1)]}
            return res


    @api.multi
    def print_report(self):
        report_action = self.env['report'].get_action(self, 'smart_hr.report_job_scale_down_model')
        data = {'ids': [], 'form': self.read([])[0]}
        report_action['data'] = data
        return report_action

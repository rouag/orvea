# -*- coding: utf-8 -*-

from openerp import api, fields, models


class WizardJobScaleDownModel(models.TransientModel):
    _name = 'wizard.job.scale.down.model'

    job_move_grade_id = fields.Many2one('hr.job.move.grade', string=u'طلب التخفيض', domain=[('move_type', '=', 'scale_down'), ('state', '!=', 'done')], required=1)
    job_id = fields.Many2one('hr.job', string=u'الوظيفة', required=1)

    @api.onchange('job_move_grade_id')
    def _onchange_job_move_grade_id(self):
        res = {}
        if self.job_move_grade_id:
            job_ids = [rec.job_id.id for rec in self.job_move_grade_id.job_movement_ids]
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

# -*- coding: utf-8 -*-

from openerp import api, fields, models


class WizardJobModifyingModel(models.TransientModel):
    _name = 'wizard.job.modifying.model'

    job_scale_up_id = fields.Many2one('hr.job.move.grade', string=u'طلب رفع', domain=[('move_type', '=', 'scale_up')])
    job_scale_down_id = fields.Many2one('hr.job.move.grade', string=u'طلب خفض', domain=[('move_type', '=', 'scale_down')])
    job_move_dep_id = fields.Many2one('hr.job.move.department', string=u'طلب نقل')
    type = fields.Selection([('scale_up', u'رفع'), ('scale_down', u'خفض'), ('move_dep', u'نقل')], default='scale_up', string=u'طبيعة التعديل')
    job_id = fields.Many2one('hr.job', string=u'الوظيفة', required=1)

    @api.onchange('type', 'job_scale_up_id', 'job_scale_down_id', 'job_move_dep_id')
    def _onchange_type(self):
        res = {}
        if self.type == 'move_dep':
            if self.job_move_dep_id:
                job_ids = [rec.job_id.id for rec in self.job_move_dep_id.job_movement_ids]
                res['domain'] = {'job_id': [('id', 'in', job_ids)]}
                return res
        if self.type == 'scale_down':
            if self.job_scale_down_id:
                job_ids = [rec.job_id.id for rec in self.job_scale_down_id.job_movement_ids]
                res['domain'] = {'job_id': [('id', 'in', job_ids)]}
                return res
        if self.type == 'scale_up':
            if self.job_scale_up_id:
                job_ids = [rec.job_id.id for rec in self.job_scale_up_id.job_movement_ids]
                res['domain'] = {'job_id': [('id', 'in', job_ids)]}
                return res
        # return empty job list
        res['domain'] = {'job_id': [('id', '=', -1)]}
        return res

    @api.multi
    def print_report(self):
        report_action = self.env['report'].get_action(self, 'smart_hr.report_job_modifying_model')
        data = {'ids': [], 'form': self.read([])[0]}
        report_action['data'] = data
        return report_action

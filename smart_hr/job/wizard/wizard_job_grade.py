# -*- coding: utf-8 -*-

from openerp import api, fields, models


class WizardJobGrade(models.TransientModel):
    _name = 'wizard.job.grade'

    grade_from_id = fields.Many2one('salary.grid.grade', string=u'مرتبة من', required=1)
    grade_to_id = fields.Many2one('salary.grid.grade', string=u'مرتبة إلى', required=1)

    @api.multi
    def print_report(self):
        report_action = self.env['report'].get_action(self, 'smart_hr.report_job_grade')
        data = {'ids': [], 'form': self.read([])[0]}
        report_action['data'] = data
        return report_action

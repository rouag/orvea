# -*- coding: utf-8 -*-

from openerp import api, fields, models
from openerp.exceptions import ValidationError

class WizardJobGrade(models.TransientModel):
    _name = 'wizard.job.grade'

    grade_from_id = fields.Many2one('salary.grid.grade', string=u'مرتبة من')
    grade_to_id = fields.Many2one('salary.grid.grade', string=u'مرتبة إلى')
    report_type = fields.Selection([('requested', u'الجارية'),
                                    ('accepted', u'الموافق عليها'),
                                    ], string=u'طلبات التخفيض', default='requested')

    @api.onchange('grade_from_id')
    def onchange_grade_from_id(self):
        if self.grade_from_id:
            res = {}
            grade_ids = []
            for rec in self.env['salary.grid.grade'].search([]):
                if int(self.grade_from_id.code) > int(rec.code):
                    grade_ids.append(rec.id)
            res['domain'] = {'grade_to_id': [('id', 'in', grade_ids)]}
            return res

    @api.multi
    def print_report(self):
        if self.report_type == 'requested' and not self.grade_from_id:
            raise ValidationError(u"الرجاء تعمير الحقل 'مرتبة من' ")
        if self.report_type == 'requested' and not self.grade_to_id:
            raise ValidationError(u"الرجاء تعمير الحقل 'مرتبة إلى'")
        report_action = self.env['report'].get_action(self, 'smart_hr.report_job_grade')
        data = {'ids': [], 'form': self.read([])[0]}
        report_action['data'] = data
        return report_action

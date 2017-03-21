# -*- coding: utf-8 -*-

from openerp import fields, models, api


class HrScholarshipSucceedWizard(models.TransientModel):

    _name = "hr.scholarship.succced.wizard"
    _description = "Scholarship Succeed Wizard"

    diploma_id = fields.Many2one('hr.employee.diploma', string=u'الشهادة', required=1, readonly=1)
    diploma_date = fields.Date(string=u'تاريخ الحصول على الشهادة', required=1, readonly=1)

    @api.multi
    def button_add_employee_education_level(self):
        cx = self.env.context or {}
        for wiz in self:
            model_obj = self.env[cx.get('active_model')]
            rec_id = model_obj.browse(cx.get('active_id'))
            employee_id = rec_id.employee_id
            self.env['hr.employee.job.education.level'].create({'level_education_id': wiz.diploma_id.education_level_id.id,
                                                                'diploma_id': wiz.diploma_id.id,
                                                                'diploma_date': wiz.diploma_date,
                                                                'employee_id': employee_id.id,
                                                                'while_serving': True,
                                                                'governmental_entity': rec_id.faculty_id.id
                                                                })
            rec_id.result = 'suceed'
            rec_id.state = 'finished'

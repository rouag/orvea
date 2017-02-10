# -*- coding: utf-8 -*-
# Part of Odoo. See LICENSE file for full copyright and licensing details.


from openerp import api, fields, models, _
from openerp.exceptions import UserError


class HrAppraisal(models.Model):
    _inherit = ['hr.appraisal']
    _description = "Employee Appraisal"
    _order = 'date_close, date_final_interview'
    _rec_name = 'employee_id'


    parent_emplyee_id  = fields.Many2one('hr.employee', string='المدير المباشر', store=True)
    parent_emplyee = fields.Boolean(string='المدير المباشر', help="This employee will be appraised by his colleagues")
    parent_emplyee_survey_id = fields.Many2one('survey.survey', string="المدير المباشر")



    @api.onchange('employee_id')
    def onchange_employee_id(self):
        if self.employee_id:
            self.department_id = self.employee_id.department_id
            self.manager_appraisal = self.employee_id.appraisal_by_manager
            self.manager_ids = self.employee_id.appraisal_manager_ids
            self.manager_survey_id = self.employee_id.appraisal_manager_survey_id
            self.colleagues_appraisal = self.employee_id.appraisal_by_colleagues
            self.colleagues_ids = self.employee_id.appraisal_colleagues_ids
            self.colleagues_survey_id = self.employee_id.appraisal_colleagues_survey_id
            self.employee_appraisal = self.employee_id.appraisal_self
            self.employee_survey_id = self.employee_id.appraisal_self_survey_id
            self.collaborators_appraisal = self.employee_id.appraisal_by_collaborators
            self.collaborators_ids = self.employee_id.appraisal_collaborators_ids
            self.collaborators_survey_id = self.employee_id.appraisal_collaborators_survey_id
            self.parent_emplyee_id=self.employee_id.parent_id

   
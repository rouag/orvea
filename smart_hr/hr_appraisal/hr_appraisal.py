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
    note_final = fields.Integer(string="نتيجة التقييم", compute='_compute_completed_survey')
    confirmed = fields.Integer(string="نتيجة التقييم", compute='_compute_completed_survey')
    adopted=fields.Boolean(string='إعتماد')
    mail_template_id = fields.Many2one('mail.template', string="Email Template for Appraisal", default=lambda self: self.env.ref('smart_hr.send_appraisal_template'))
    
    @api.multi
    def _compute_note_final(self):
        completed_survey = self.env['survey.user_input'].read_group([('appraisal_id', 'in', self.ids), ('state', '=', 'done')], ['appraisal_id'], ['appraisal_id'])
        print 222222,completed_survey
        for appraisal in self:
            appraisal.note_final = completed_survey.quizz_score
            



    @api.onchange('employee_id')
    def onchange_employee_ids(self):
        if self.employee_id:
            self.parent_emplyee_id=self.employee_id.parent_id


# class survey_question_inherite(models.Model):
#     ''' Questions that will be asked in a survey.
# 
#     Each question can have one of more suggested answers (eg. in case of
#     dropdown choices, multi-answer checkboxes, radio buttons...).'''
#     _inherit = ['survey.question']
#     _rec_name = 'question'
#     _order = 'sequence,id'
# 
#     # Model fields #
# 
# 
#        
#         # Answer
#     types= fields.Selection([
#                 ('simple_choice', 'Multiple choice: only one answer'),
#                 ('multiple_choice', 'Multiple choice: multiple answers allowed'),
#                 ('matrix', 'Matrix')], 'Type of Question', size=15, required=1),
#    
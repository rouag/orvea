# -*- coding: utf-8 -*-


from openerp import models, fields, api, _


class HrDecision(models.Model):
    _name = 'hr.decision'
    _inherit = ['mail.thread']
    _description = u'القرار'

    name = fields.Char(string='قرار إداري رقم', required=1)
    decision_type_id = fields.Many2one('hr.decision.type', string='نوع القرار', required=1)
    date = fields.Date(string='بتاريخ', required=1)
    employee_id=fields.Many2one('hr.employee',string='الموظف',required=1,)
    text = fields.Html(string='نص القرار')
    
#     decision_appoint_id = Many2one('hr.decision.appoint')
#     job_id=fields.Many2one(related='decision_appoint_id.job_id', store=True, readonly=True, string='الوظيفة')
#     number_job=fields.Many2one(related='decision_appoint_id.number_job', store=True, readonly=True, string='الرقم الوظيفي')
#     type_id=fields.Many2one(related='decision_appoint_id.type_id', store=True, readonly=True, string='الصنف')
#        department_id=fields.Many2one(related='decision_appoint_id.department_id', store=True, readonly=True, string='القسم')
#     grade_id=fields.Many2one(related='decision_appoint_id.grade_id', store=True, readonly=True, string='المرتبة')
#     basic_salary=fields.Many2one(related='decision_appoint_id.basic_salary', store=True, readonly=True, string='الراتب الأساسي')
#     net_salary=fields.Many2one(related='decision_appoint_id.net_salary', store=True, readonly=True, string='صافي الراتب')
#     degree_id=fields.Many2one(related='decision_appoint_id.degree_id', store=True, readonly=True, string='الدرجة')
#   
    
    
           

    @api.onchange('decision_type_id')
    def onchange_decision_type_id(self):
        
         employee_line = self.env['hr.decision.appoint'].search([('employee_id', '=', self.employee_id.id),('state', '=', 'done')])
         if employee_line and self.decision_type_id :
                    
            decision_type_line = self.env['hr.decision.type'].search([('id', '=', self.decision_type_id.id)
                                                ])
            if decision_type_line :
                    employee = self.employee_id.name or ""
                    dattz = self.date or ""
                    carte_id = self.employee_id.identification_id or ""
                    numero = self.name or ""
                    job_id = employee_line.job_id.name.name or ""
                    number = employee_line.job_id.name.number or ""
                    code = employee_line.number_job or ""
                    department_id = employee_line.department_id.name or ""
                    type_job_id = employee_line.type_id.name or ""
                    grade_id = employee_line.grade_id.name or ""
                    degree_id = employee_line.degree_id.name or ""
                    salary = employee_line.basic_salary   or ""
                    transport_allow = employee_line.transport_allow or ""
                    retirement = employee_line.retirement or ""
                    net_salary = employee_line.net_salary or ""
                    
                    if decision_type_line.text:
                        rel_text = decision_type_line.text
                        rep_text = rel_text.replace('EMPLOYEE',unicode(employee))
                        rep_text = rep_text.replace('DATE',unicode(dattz))
                        rep_text = rep_text.replace('CARTEID',unicode(carte_id))
                        rep_text = rep_text.replace('NUMERO',unicode(numero))
                        rep_text = rep_text.replace('JOB',unicode(job_id))
                        rep_text = rep_text.replace('CODE',unicode(code))
                        rep_text = rep_text.replace('DEGREE',unicode(degree_id))
                        rep_text = rep_text.replace('GRADE',unicode(grade_id))
                        rep_text = rep_text.replace('BASICSALAIRE',unicode(salary))
                        rep_text = rep_text.replace('DEPARTEMENT',unicode(department_id))
                        self.text = rep_text
                
class HrDecisionType(models.Model):
    _name = 'hr.decision.type'
    _description = u'نوع القرار'

    name = fields.Char(string='المسمى', required=1)
    code = fields.Char(string='الرمز')
    note = fields.Text(string='ملاحظات')
    text = fields.Html(string='نص القرار')

#     @api.multi
#     def name_get(self):
#         result = []
#         for record in self:
#             name = '[%s] %s' % (record.code, record.name)
#             result.append((record.id, name))
#         return result

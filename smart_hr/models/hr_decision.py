# -*- coding: utf-8 -*-


from openerp import models, fields, api, _


class HrDecision(models.Model):
    _name = 'hr.decision'
    _inherit = ['mail.thread']
    _description = u'القرار'

    name = fields.Char(string='المسمى', required=1)
    decision_type_id = fields.Many2one('hr.decision.type', string='نوع القرار', required=1)
    date = fields.Date(string='التاريخ', required=1)
    employee_id=fields.Many2one('hr.employee',string='الموظف',required=1,)
    text = fields.Html(string='نص القرار')

    @api.onchange('decision_type_id')
    def onchange_decision_type_id(self):
        if self.decision_type_id:
            decision_type_line = self.env['hr.decision.type'].search([('id', '=', self.decision_type_id.id)
                                                ])
           # employee=self.employee_id.id
           # employe=str(employee)
          #  print"employe",employee
            if decision_type_line.text:
                rel_text=decision_type_line.text
                rep_text=rel_text.replace('EMPLOYE','123456' )
                
                self.text = rep_text
                print"text",self.text
                
class HrDecisionType(models.Model):
    _name = 'hr.decision.type'
    _description = u'نوع القرار'

    name = fields.Char(string='المسمى', required=1)
    code = fields.Char(string='الرمز')
    note = fields.Text(string='ملاحظات')
    text = fields.Html(string='نص القرار')

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = '[%s] %s' % (record.code, record.name)
            result.append((record.id, name))
        return result

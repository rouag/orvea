# -*- coding: utf-8 -*-

from openerp import api, fields, models, _


class WizardSanctionAction(models.TransientModel):
    _name = 'wizard.sanction.action'

    name = fields.Char(string='رقم القرار')
    order_date = fields.Date(string='تاريخ القرار')
    employee_id = fields.Many2one('hr.employee', string=u' إسم الموظف')
    reason = fields.Text(string='السبب')
    state = fields.Selection([
                              ('draft', u'طلب'),
                              ('waiting', u'  صاحب صلاحية العقوبات'),
                              ('done', u'اعتمدت'),
                              ('refuse', u'رفض'),
                             
                              ], string=u'حالة', default='draft', advanced_search=True)




    @api.multi
    def action_draft(self):
        self.ensure_one()
        
        self.state = 'waiting'
  
    @api.multi
    def action_refuse(self):
        self.ensure_one()
        self.state = 'draft'
    
    @api.multi
    def action_waiting(self):
        self.ensure_one()
        self.state = 'done'      


    @api.multi
    def action_exclusion(self):
        sanction_line_id = self._context.get('active_id', False)
        if sanction_line_id:
            sanction_line = self.env['hr.sanction.ligne'].browse(sanction_line_id)
            diff_line = self.env['hr.difference.sanction'].search([('employee_id', '=', sanction_line.employee_id.id), ( 'type_sanction_new','=',sanction_line.sanction_id.id)])
            val = {
                'sanction_id': sanction_line.sanction_id.id,
                'employee_id': sanction_line.employee_id.id,
               'name' : self.name,
                'reason': self.reason,
                'order_date': self.order_date,
                'action': u'إستبعاد موظف'
            }
            sanction_line.state = 'excluded'
            self.env['hr.sanction.history'].create(val)
            if diff_line :
                diff_line.state = 'excluded'
                diff_line.write({'state': 'excluded'})
        return {'type': 'ir.actions.act_window_close'}

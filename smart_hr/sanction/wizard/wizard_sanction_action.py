# -*- coding: utf-8 -*-

from openerp import api, fields, models, _


class WizardSanctionAction(models.TransientModel):
    _name = 'wizard.sanction.action'

    name = fields.Char(string='رقم قرار التعديل', required=1)
    order_date = fields.Date(string='تاريخ قرار التعديل', required=1)
    employee_id = fields.Many2one('hr.employee', string=u' إسم الموظف')
    reason = fields.Text(string='السبب')
    days_number = fields.Integer(string='عدد أيام ')
    amount = fields.Integer(string='مبلغ')

    @api.multi
    def action_exclusion(self):
        active_model = self._context.get('active_model', False)
        active_id = self._context.get('active_id', False)
        action = self._context.get('action', False)
        print '---------',active_model,active_id,action
        if active_model == 'hr.sanction.ligne' and active_id:
            sanction_line = self.env['hr.sanction.ligne'].browse(active_id)
            description = ''
            field_updated = ''
            if sanction_line.days_number != self.days_number :
                field_updated += u'عدد أيام من %s  إلى %s' % (sanction_line.days_number, self.days_number)
            if sanction_line.amount != self.amount:
                field_updated += u'مبلغ من %s  إلى %s' % (sanction_line.amount, self.amount)
            if action == 'exclusion':
                description = u'إستبعاد موظف'
            elif action == 'update'  :
                description = u'تعديل عقوبة : ' + field_updated
            val = {
                'sanction_id': sanction_line.sanction_id.id,
                'employee_id': sanction_line.employee_id.id,
                'name': self.name,
                'reason': self.reason,
                'order_date': self.order_date,
                'action': description
            }
            if action == 'exclusion':
                sanction_line.state = 'excluded'
            elif action == 'update':
                if sanction_line.days_number != self.days_number and sanction_line.deduction == False and sanction_line.days_difference == 0 :
                   # sanction_line.days_difference = sanction_line.days_difference + compt_diff
                    sanction_line.days_number = self.days_number
                if sanction_line.days_number != self.days_number and sanction_line.deduction == False and sanction_line.days_difference != 0 :
                    compt_dif = sanction_line.days_number - self.days_number
                    sanction_line.days_difference = sanction_line.days_difference + compt_dif
                    sanction_line.days_number = self.days_number
                    
                if sanction_line.days_number != self.days_number and sanction_line.deduction == True and sanction_line.days_difference == 0 :
                    compt_dif =  -sanction_line.days_number 
                    sanction_line.days_difference = sanction_line.days_number - self.days_number + compt_dif
                    sanction_line.days_number = self.days_number
                    sanction_line.deduction = False
                if sanction_line.days_number != self.days_number and sanction_line.deduction == True and sanction_line.days_difference != 0 :
                    compt_dif = sanction_line.days_number - sanction_line.days_difference
                    sanction_line.days_difference = compt_dif
                    sanction_line.days_number = compt_dif -self.days_number 
                  
                    sanction_line.deduction = False
               
                
                if sanction_line.amount != self.amount and sanction_line.deduction == True :
                    sanction_line.amount_difference = sanction_line.amount - self.amount
                    sanction_line.amount = self.amount
            self.env['hr.sanction.history'].create(val)

        elif active_model == 'hr.sanction' and active_id:
            sanction = self.env['hr.sanction'].browse(active_id)
            field_updated = ''
            if self.days_number and sanction.type_sanction.deduction == True :
                field_updated += u'عدد أيام : %s ' % self.days_number
            if self.amount and sanction.type_sanction.deduction == True :
                field_updated += u'مبلغ : %s ' % self.amount
            description = u'تعديل العقوبة لجميع الموظفين ' + field_updated
            val = {
                'sanction_id': sanction.id,
                'name': self.name,
                'reason': self.reason,
                'order_date': self.order_date,
                'action': description
            }
            if self.days_number and sanction.type_sanction.deduction == True :
                for line in sanction.line_ids:
                    line.days_difference = line.days_number - self.days_number
                    line.days_number = self.days_number
            if self.amount and sanction.type_sanction.deduction == True :
                for line in sanction.line_ids:
                    line.amount_difference = line.amount - self.amount
                    line.amount = self.amount
            self.env['hr.sanction.history'].create(val)

        return {'type': 'ir.actions.act_window_close'}

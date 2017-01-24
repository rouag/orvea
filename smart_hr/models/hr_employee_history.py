# -*- coding: utf-8 -*-


from openerp import models, fields, api, _



class HrEmployeeHistory(models.Model):
    _name = 'hr.employee.history'
    _description = u'سجل الاجراءات' 


    employee_id = fields.Many2one('hr.employee', string=u'الموظف', required=1)
    date = fields.Date(string=u'التاريخ')
    num_decision = fields.Char(string=u'رقم القرار')
    date_decision = fields.Date(string=u'تاريخ القرار')
    type = fields.Selection([('appoint', u'تعيين'),
                             ('promotion', u' ترقية'),
                             ('deputation', u' انتداب'),
                             ('suspension', u' كف يد'),
                             ('termination', u' طي قيد'),
                             ('training', u' تدريب'),
                             ('termination', u' طي قيد'),
                             ('creation', u' انشاء موظف'),
                             ('deduction', u' حسميات'),
                             ], string=u'نوع الاجرا ء')

# -*- coding: utf-8 -*-


from openerp import models, fields, api, _



class HrEmployeeFunctionnalCard(models.Model):
    _name = 'hr.employee.functionnal.card'
    _description = u'بطاقة وظيفية' 

    employee_id = fields.Many2one('hr.employee', string=u'الموظف', required=1)
    number = fields.Char(string=u'الرقم الوظيفي', related="employee_id.number")


class HrEmployeeIssuingFunctionnalCard(models.Model):
    _name = 'hr.employee.issuing.functionnal.card'
    _description = u'اصدار بطاقة وظيفية' 

    employee_ids = fields.Many2many('hr.employee', string=u'الموظف', required=1)    
    date = fields.Date(string=u'التاريخ من ', default=fields.Datetime.now(), readonly=1)
    expiration_date = fields.Date(string=u'التاريخ من ')
    state = fields.Selection([
        ('draft', u'طلب'),
        ('hrm', u'مدير شؤون الموظفين'),
       ('done', u'اعتمدت'),
        ('refuse', u'رفض'),
 ], string=u'حالة', default='draft', advanced_search=True)


    @api.multi
    def button_accept_hrm(self):
        self.ensure_one()
        self.state = 'done'

    @api.multi
    def button_send_request(self):
        self.ensure_one()
        self.state = 'hrm'

    @api.multi
    def button_refuse_hrm(self):
        self.ensure_one()
        self.state = 'refuse'


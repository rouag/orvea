# -*- coding: utf-8 -*-

from openerp import models, api, fields, _
from openerp.exceptions import ValidationError


class hrEmployeesituation(models.Model):
    _name = 'hr.employee.situation.order'
    _rec_name = 'employee_id'
    
    date = fields.Date(string=u'التاريخ ', default=fields.Datetime.now(), readonly=1)
    employee_id = fields.Many2one('hr.employee', string='الموظف', required=1)
    hospital_name = fields.Many2one('res.partner', string=u'المستشفى ', required=1, domain="[('company_type','=','hospital')]")
    date_hospitalisation = fields.Date(string=u'تاريخ مراجعةا لمستشفى ', default=fields.Datetime.now(), required=1)

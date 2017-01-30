# -*- coding: utf-8 -*-

from openerp import models, api, fields, _
from openerp.exceptions import ValidationError


class hrEmployeesituation(models.Model):
    _name = 'hr.employee.situation.order'
    _rec_name = 'employee_id'

    employee_id = fields.Many2one('hr.employee', string=' إسم الموظف', required=1)
    date = fields.Date(string=u'تاريخ ', default=fields.Datetime.now(),readonly=1)
    hospital_name = fields.Char(string=u'المستشفى ', required=1)
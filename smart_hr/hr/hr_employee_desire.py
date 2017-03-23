# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from datetime import date, datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class HrEmployeeDesire(models.Model):
    _name = 'hr.employee.desire'
    _description = u'رغبات النقل'
    _order = 'sequence'

    name = fields.Char(string=u'المسمى')
    sequence = fields.Integer(string=u'الرقم التسلسلي', default=1)
    employee_id = fields.Many2one('hr.employee.transfert',  string=u'الموظف')

# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from openerp.exceptions import Warning
from openerp.exceptions import ValidationError

class HrSickHolidaysPeriods(models.Model):

    _name = 'hr.sick.holidays.periods'
    _description = 'فترات الإجازات المرضيّة'

    employee_id = fields.Many2one('hr.employee', string=u'الموظف')
    date_from = fields.Date(string=u'التاريخ من')
    date_to = fields.Date(string=u'التاريخ الى')
    Counter =fields.Integer(string=u'عداد')

class HrSickHolidays(models.Model):

    _name = 'hr.sick.holidays'
    _name = 'الإجازات المرضيّة'

    date_from = fields.Date(string=u'التاريخ من')
    date_to = fields.Date(string=u'التاريخ الى')
    duration =fields.Integer(string=u'عداد')
    period_id = fields.Many2one('hr.sick.holidays.periods', string=u'فترة الإجازة')


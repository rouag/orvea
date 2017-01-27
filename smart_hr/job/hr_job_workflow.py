# -*- coding: utf-8 -*-


from openerp import models, fields, api, _
from openerp.exceptions import Warning
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from datetime import date, datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class HrJobWorflow(models.Model):
    _name = 'hr.job.workflow'
    _description = u'المخطط الإنسيابي'

    name = fields.Char(string=u'مسمى الإجراء', required=1, readonly=1)
    state_ids = fields.Many2many('hr.job.workflow.state', string=u'المخطط الإنسيابي')


class HrJobWorflowState(models.Model):
    _name = 'hr.job.workflow.state'
    name = fields.Char(string=u'إسم الحالة')
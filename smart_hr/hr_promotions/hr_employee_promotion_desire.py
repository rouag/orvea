# -*- coding: utf-8 -*-

from openerp import models, fields, api, _
from dateutil.relativedelta import relativedelta
from openerp.exceptions import ValidationError
from datetime import date, datetime, timedelta
from openerp.tools import DEFAULT_SERVER_DATE_FORMAT, DEFAULT_SERVER_DATETIME_FORMAT


class HrEmployeePromotionDesire(models.Model):
    _name = 'hr.employee.promotion.desire'
    _description = u'رغبات الترقية'
    _order = 'sequence'

    name = fields.Char(string=u'المسمى', required =1)
    sequence = fields.Integer(string=u'الرقم التسلسلي', default=1)
    demande_promotion_id = fields.Many2one('hr.promotion.employee.demande', string=u'طلب الترقية  ')

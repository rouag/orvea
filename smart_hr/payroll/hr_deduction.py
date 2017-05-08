# -*- coding: utf-8 -*-

from openerp import models, api, fields, _
from openerp.exceptions import ValidationError
from dateutil import relativedelta
import time as time_date
from datetime import datetime
from openerp.addons.smart_base.util.umalqurra import *
from umalqurra.hijri_date import HijriDate
from umalqurra.hijri import Umalqurra


class HrDeductionType(models.Model):
    _name = 'hr.deduction.type'
    _description = u'أنواع الحسميات'

    name = fields.Char(string=' الوصف', required=1)
    code = fields.Char(string='الرمز', required=1)
    type = fields.Selection([('retard_leave', 'تأخير وخروج'), ('absence', 'غياب'), ('sanction', 'عقوبة')], string='النوع', required=1)

    @api.multi
    def name_get(self):
        result = []
        for record in self:
            name = '[%s] %s' % (record.code, record.name)
            result.append((record.id, name))
        return result
